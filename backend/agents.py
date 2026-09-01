from langchain_core.messages import HumanMessage, SystemMessage
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
    model = ChatOllama(model=settings.default_model, temperature=0.2)
    tools = _toolset(profile)
    return model.bind_tools(tools), tools, profile


async def run_local_agent(message: str, task: str | None = None) -> str:
    model, tools, profile = build_local_agent(task)
    tool_map = {tool.name: tool for tool in tools}
    memory = build_memory_context(profile.memory_scope)
    system = (
        f"{SYSTEM_PROMPT}\n\nTASK: {profile.name}\n"
        f"TASK DESCRIPTION: {profile.description}\n\n"
        f"RELEVANT MEMORY:\n{memory}"
    )
    messages = [SystemMessage(content=system), HumanMessage(content=message)]

    for _ in range(5):
        response = await model.ainvoke(messages)
        messages.append(response)

        if not getattr(response, "tool_calls", None):
            return response.content if isinstance(response.content, str) else str(response.content)

        for call in response.tool_calls:
            tool = tool_map.get(call["name"])
            if tool is None:
                continue
            result = await tool.ainvoke(call["args"])
            messages.append(result)

    return "I couldn't complete the tool workflow within the allowed steps."
