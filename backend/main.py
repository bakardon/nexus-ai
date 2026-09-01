from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .agents import run_local_agent
from .config import get_settings
from .providers import ProviderError, chat
from .router import choose_route
from .task_registry import get_task_profile, load_task_profiles

app = FastAPI(title="NEXUS AI", version="0.5.0")


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    task: str | None = None
    provider: str | None = None
    model: str | None = None
    use_tools: bool = True


class ChatResponse(BaseModel):
    response: str
    task: str
    provider: str
    model: str
    route_reason: str
    approval_required: bool


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/tasks")
async def tasks() -> list[dict]:
    return [profile.__dict__ for profile in load_task_profiles().values()]


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    settings = get_settings()
    profile = get_task_profile(request.task)
    route = choose_route(profile.name)
    provider = request.provider or route.provider
    model = request.model or route.model or settings.default_model

    try:
        if request.use_tools and provider == "ollama":
            response = await run_local_agent(request.message, profile.name)
        else:
            response = await chat(
                [{"role": "user", "content": request.message}],
                provider=provider,
                model=model,
            )
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent error: {exc}") from exc

    return ChatResponse(
        response=response,
        task=profile.name,
        provider=provider,
        model=model,
        route_reason=route.reason,
        approval_required=profile.approval_required,
    )
