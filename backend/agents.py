from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from .config import get_settings
from .tools.calculator import calculator
from .tools.search import web_search

SYSTEM_PROMPT = """You are NEXUS, a practical personal intelligence assistant.

Your job is to give useful, honest, evidence-aware answers.
Use tools when current information or arithmetic is needed.
Do not invent facts or sources. Clearly separate known facts, assumptions,
and recommendations. For decisions, present the strongest case for and
against before giving a conclusion.
"""


def build_local_agent():
    settings = get_settings()
    model = ChatOllama(model=settings.default_model, temperature=0.2)
    tools = [web_search, calculator]
    return model.bind_tools(tools), tools


async def run_local_agent(message: str) -> str:
    model, tools = build_local_agent()
    tool_map = {tool.name: tool for tool in tools}
    messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=message)]

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
