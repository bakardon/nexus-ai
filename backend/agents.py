from collections.abc import Awaitable, Callable
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_ollama import ChatOllama

from .config import get_settings
from .memory import build_memory_context
from .task_registry import TaskProfile, get_task_profile
from .tools.calculator import calculator
from .tools.search import web_search

SYSTEM_PROMPT = """You are NEXUS, a practical personal intelligence assistant.

Give useful, honest, evidence-aware answers. Use tools when current information
or arithmetic is needed. Never invent sources. Separate facts, assumptions,
and recommendations. For decisions, present the strongest case for and against.

The user can define task-specific profiles. Follow the selected task's scope and
never use a tool outside that profile.
"""


def _toolset(profile: TaskProfile):
    available = {
        "web_search": web_search,
        "calculator": calculator,
    }
    return [available[name] for name in profile.tools if name in available]


def build_local_agent(task: str | None = None):
    settings = get_settings()
    profile = get_task_profile(task)
    model = ChatOllama(
        model=settings.default_model,
        base_url=settings.ollama_base_url,
        temperature=0.2,
    )
    tools = _toolset(profile)
    return model.bind_tools(tools), tools, profile


async def run_local_agent(
    message: str,
    task: str | None = None,
    workspace_id: str | None = None,
    *,
    memory_query: str = "",
    on_tool_event: Callable[[dict[str, Any]], Awaitable[None] | None] | None = None,
) -> str:
    settings = get_settings()
    model, tools, profile = build_local_agent(task)
    tool_map = {tool.name: tool for tool in tools}
    memory = build_memory_context(profile.memory_scope, workspace_id, memory_query or message)
    personality = settings.personality_file.read_text(encoding="utf-8")
    system = (
        f"{SYSTEM_PROMPT}\n\nPERSONALITY:\n{personality}\n\nTASK: {profile.name}\n"
        f"TASK DESCRIPTION: {profile.description}\n\n"
        f"RELEVANT MEMORY:\n{memory or 'No relevant user memory is available.'}"
    )
    messages = [SystemMessage(content=system), HumanMessage(content=message)]

    for _ in range(settings.max_agent_steps):
        response = await model.ainvoke(messages)
        messages.append(response)

        if not getattr(response, "tool_calls", None):
            return response.content if isinstance(response.content, str) else str(response.content)

        for call in response.tool_calls:
            tool = tool_map.get(call["name"])
            if tool is None:
                raise RuntimeError(f"Model requested unavailable tool: {call['name']}")
            await _notify(
                on_tool_event,
                {"tool": tool.name, "status": "in_progress", "arguments": call["args"]},
            )
            try:
                result = await tool.ainvoke(call["args"])
            except Exception as exc:
                await _notify(
                    on_tool_event,
                    {"tool": tool.name, "status": "failed", "detail": str(exc)},
                )
                raise
            await _notify(
                on_tool_event,
                {"tool": tool.name, "status": "completed", "result": str(result)[:2000]},
            )
            messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))

    return "I couldn't complete the tool workflow within the allowed steps."


async def _notify(
    callback: Callable[[dict[str, Any]], Awaitable[None] | None] | None, event: dict[str, Any]
) -> None:
    if callback is None:
        return
    result = callback(event)
    if hasattr(result, "__await__"):
        await result
