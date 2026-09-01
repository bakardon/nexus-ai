from typing import Any

import httpx

from .config import get_settings


class ProviderError(RuntimeError):
    pass


async def _openai_compatible_chat(
    *,
    base_url: str,
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
) -> str:
    if not api_key:
        raise ProviderError("API key is not configured")

    payload = {"model": model, "messages": messages, "temperature": 0.2}
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{base_url.rstrip('/')}/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise ProviderError(f"Hosted provider request failed: {exc}") from exc

    data: dict[str, Any] = response.json()
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ProviderError("Provider returned an unexpected response") from exc


async def ollama_chat(messages: list[dict[str, str]], model: str) -> str:
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

    data: dict[str, Any] = response.json()
    try:
        return data["message"]["content"]
    except (KeyError, TypeError) as exc:
        raise ProviderError("Ollama returned an unexpected response") from exc


async def chat(
    messages: list[dict[str, str]],
    provider: str | None = None,
    model: str | None = None,
) -> str:
    settings = get_settings()
    selected_provider = (provider or settings.default_provider).lower()
    selected_model = model or settings.default_model

    if selected_provider == "ollama":
        return await ollama_chat(messages, selected_model)

    if selected_provider == "groq":
        return await _openai_compatible_chat(
            base_url="https://api.groq.com/openai/v1",
            api_key=settings.groq_api_key,
            model=selected_model,
            messages=messages,
        )

    if selected_provider == "openrouter":
        return await _openai_compatible_chat(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.openrouter_api_key,
            model=selected_model,
            messages=messages,
        )

    raise ProviderError(f"Unknown provider: {selected_provider}")
