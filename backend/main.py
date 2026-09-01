from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .config import get_settings
from .providers import ProviderError, chat
from .router import choose_route

app = FastAPI(title="NEXUS AI", version="0.2.0")


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    task: str | None = None
    provider: str | None = None
    model: str | None = None


class ChatResponse(BaseModel):
    response: str
    provider: str
    model: str
    route_reason: str


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    settings = get_settings()
    route = choose_route(request.task)
    provider = request.provider or route.provider
    model = request.model or route.model or settings.default_model

    try:
        response = await chat(
            [{"role": "user", "content": request.message}],
            provider=provider,
            model=model,
        )
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return ChatResponse(
        response=response,
        provider=provider,
        model=model,
        route_reason=route.reason,
    )
