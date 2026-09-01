from dataclasses import asdict

from .capabilities import require_available_capabilities
from .task_intent import infer_intent
from .task_registry import get_task_profile
from .workspace import (
    TaskWorkspace,
    create_workspace,
    get_workspace,
    save_workspace,
    transition_workspace,
)


class TaskEngineError(RuntimeError):
    pass


def start_task(message: str, requested_task_type: str | None = None) -> tuple[TaskWorkspace, dict]:
    intent = infer_intent(message)
    profile = get_task_profile(requested_task_type or intent.task_type)
    workspace = create_workspace(intent.objective, profile.name)

    requested = list(profile.tools)
    capabilities = require_available_capabilities(requested)

    plan = {
        "intent": asdict(intent),
        "objective": workspace.objective,
        "tools": requested,
        "capabilities": [cap.name for cap in capabilities],
        "requires_approval": profile.approval_required,
        "memory_scope": profile.memory_scope,
        "steps": [
            {"id": "understand", "description": "Understand the objective", "status": "completed"},
            {
                "id": "execute",
                "description": "Use the local model and allowed capabilities",
                "status": "planned",
            },
            {
                "id": "review",
                "description": "Review the output and its verification state",
                "status": "planned",
            },
        ],
    }
    workspace.plan = plan
    transition_workspace(workspace, "planned", "Workspace created and execution plan prepared")
    save_workspace(workspace)
    return workspace, workspace.plan


def require_workspace(workspace_id: str) -> TaskWorkspace:
    workspace = get_workspace(workspace_id)
    if workspace is None:
        raise TaskEngineError(f"Unknown workspace: {workspace_id}")
    return workspace
