from dataclasses import asdict

from fastapi import FastAPI, HTTPException

from .agents import run_local_agent
from .api_models import ChatRequest, TaskRunRequest, WorkspaceRequest
from .config import get_settings
from .providers import ProviderError, chat
from .task_engine import TaskEngineError, start_task
from .task_registry import get_task_profile, load_task_profiles
from .verification import inspect_output
from .workspace import (
    get_workspace,
    record_event,
    save_workspace,
    transition_workspace,
    update_plan_step,
)

app = FastAPI(title="NEXUS AI", version="0.7.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/tasks")
async def tasks() -> list[dict]:
    return [profile.__dict__ for profile in load_task_profiles().values()]


@app.post("/api/tasks/start")
async def create_task(request: WorkspaceRequest) -> dict:
    try:
        workspace, plan = start_task(request.objective, request.task_type)
    except (TaskEngineError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"workspace": asdict(workspace), "plan": plan}


@app.get("/api/tasks/{workspace_id}")
async def get_task(workspace_id: str) -> dict:
    workspace = get_workspace(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return asdict(workspace)


@app.post("/api/tasks/{workspace_id}/run")
async def run_task(workspace_id: str, request: TaskRunRequest) -> dict:
    return await _execute_task(workspace_id, request)


@app.post("/api/tasks/{workspace_id}/resume")
async def resume_task(workspace_id: str, request: TaskRunRequest) -> dict:
    return await _execute_task(workspace_id, request, resuming=True)


async def _execute_task(
    workspace_id: str, request: TaskRunRequest, *, resuming: bool = False
) -> dict:
    workspace = get_workspace(workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")

    try:
        profile = get_task_profile(workspace.task_type)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    if profile.approval_required and not request.approved:
        transition_workspace(workspace, "awaiting_approval", "Execution is waiting for approval")
        save_workspace(workspace)
        raise HTTPException(
            status_code=409,
            detail="This task requires explicit approval before execution.",
        )

    settings = get_settings()
    if settings.default_provider != "ollama":
        transition_workspace(
            workspace,
            "failed",
            "Configured provider cannot execute the local task lifecycle",
            provider=settings.default_provider,
        )
        update_plan_step(workspace, "execute", "failed", "A local Ollama provider is required")
        save_workspace(workspace)
        raise HTTPException(
            status_code=409,
            detail="Task execution currently supports the configured local Ollama provider only.",
        )

    transition_workspace(
        workspace,
        "in_progress",
        "Resuming workspace execution" if resuming else "Starting workspace execution",
    )
    update_plan_step(workspace, "execute", "in_progress")
    save_workspace(workspace)

    tool_events: list[dict] = []

    async def record_tool_event(event: dict) -> None:
        tool_events.append(event)
        record_event(
            workspace,
            "in_progress" if event["status"] != "failed" else "failed",
            f"Tool {event['tool']} {event['status']}",
            **{key: value for key, value in event.items() if key not in {"tool", "status"}},
        )
        save_workspace(workspace)

    try:
        response = await run_local_agent(
            request.message,
            profile.name,
            workspace.id,
            memory_query=f"{workspace.objective}\n{request.message}",
            on_tool_event=record_tool_event,
        )
    except ProviderError as exc:
        transition_workspace(
            workspace, "failed", "Local model provider request failed", error=str(exc)
        )
        update_plan_step(workspace, "execute", "failed", str(exc))
        save_workspace(workspace)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        transition_workspace(workspace, "failed", "Task execution failed", error=str(exc))
        update_plan_step(workspace, "execute", "failed", str(exc))
        save_workspace(workspace)
        raise HTTPException(status_code=500, detail=f"Task execution failed: {exc}") from exc

    verification = inspect_output(response, tool_events)
    update_plan_step(workspace, "execute", "completed")
    update_plan_step(workspace, "review", verification.status, verification.note)
    workspace.verification_status = verification.status
    transition_workspace(
        workspace,
        "completed" if verification.execution_ok else "failed",
        verification.note,
    )
    save_workspace(workspace)

    from .memory import append_task_memory

    append_task_memory(
        workspace.id,
        f"Run result ({verification.status}): {response[:4000]}",
    )
    return {
        "workspace": asdict(workspace),
        "response": response,
        "capabilities": list(profile.tools),
        "verified": verification.verified,
        "verification_status": verification.status,
        "verification_note": verification.note,
    }


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest) -> dict:
    settings = get_settings()
    try:
        profile = get_task_profile(request.task)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    provider = request.provider or settings.default_provider
    model = request.model or settings.default_model

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
        "route_reason": "explicit request" if request.provider else "configured default provider",
        "approval_required": profile.approval_required,
    }
