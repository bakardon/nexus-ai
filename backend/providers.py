from collections.abc import AsyncIterator

import httpx

from .config import get_settings


class ProviderError(RuntimeError):
    pass


async def ollama_chat(messages: list[dict], model: str) -> str:
    settings = get_settings()
    payload = {"model": model, "messages": messages, "stream": False}

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{settings.ollama_base_url.rstrip('/')}/api/chat",
                json=payload,
            )
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise ProviderError(f"Ollama request failed: {exc}") from exc

    data = response.json()
    return data.get("message", {}).get("content", "")


async def chat(messages: list[dict], provider: str | None = None, model: str | None = None) -> str:
    settings = get_settings()
    selected_provider = provider or settings.default_provider
    selected_model = model or settings.default_model

    if selected_provider == "ollama":
        return await ollama_chat(messages, selected_model)

    raise ProviderError(
        f"Provider '{selected_provider}' is not implemented yet. "
        "MVP currently supports Ollama; hosted providers are next."
    )
