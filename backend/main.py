from dataclasses import asdict

from fastapi import FastAPI, HTTPException

from .agents import run_local_agent
from .api_models import ApprovalRequest, ChatRequest, WorkspaceRequest
from .config import get_settings
from .providers import ProviderError, chat
from .router import choose_route
from .task_engine import start_task
from .task_registry import get_task_profile, load_task_profiles
from .workspace import get_workspace

app = FastAPI(title="NEXUS AI", version="0.6.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/tasks")
async def tasks() -> list[dict]:
    return [profile.__dict__ for profile in load_task_profiles().values()]


@app.post("/api/tasks/start")
async def create_task(request: WorkspaceRequest) -> dict:
    workspace, plan = start_task(request.objective)
    return {"workspace": asdict(workspace), "plan": plan}


@app.get("/api/tasks/{workspace_id}")
async def get_task(workspace_id: str) -> dict:
    workspace = get_workspace(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return asdict(workspace)


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest) -> dict:
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

    return {
        "response": response,
        "task": profile.name,
        "provider": provider,
        "model": model,
        "route_reason": route.reason,
        "approval_required": profile.approval_required,
    }
