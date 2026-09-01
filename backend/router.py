from dataclasses import dataclass


@dataclass(frozen=True)
class Route:
    provider: str
    model: str
    reason: str


def choose_route(task: str | None = None) -> Route:
    """Small deterministic router for the MVP.

    The router is deliberately simple now; an LLM-based router and health-aware
    fallback chain will be added once provider adapters are tested.
    """
    normalized = (task or "general").lower()

    if normalized in {"research", "web"}:
        return Route("openrouter", "", "research can use a hosted model")

    if normalized in {"reasoning", "decision"}:
        return Route("groq", "", "reasoning can use a fast hosted model")

    return Route("ollama", "llama3.2", "local model is the default fallback")
