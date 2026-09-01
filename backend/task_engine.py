from dataclasses import asdict

from .capabilities import capability_status
from .memory import build_memory_context
from .task_intent import infer_intent
from .task_registry import get_task_profile
from .workspace import TaskWorkspace, create_workspace, get_workspace


class TaskEngineError(RuntimeError):
    pass


def start_task(message: str) -> tuple[TaskWorkspace, dict]:
    intent = infer_intent(message)
    profile = get_task_profile(intent.task_type)
    workspace = create_workspace(intent.objective, intent.task_type)

    requested = list(profile.tools)
    capabilities = [capability_status(name) for name in requested]
    unavailable = [cap.name for cap in capabilities if cap is not None and not cap.available]

    plan = {
        "intent": asdict(intent),
        "workspace": workspace.id,
        "tools": requested,
        "unavailable_tools": unavailable,
        "requires_approval": profile.approval_required,
        "memory_scope": profile.memory_scope,
        "memory": build_memory_context(profile.memory_scope, workspace.id),
    }
    return workspace, plan


def require_workspace(workspace_id: str) -> TaskWorkspace:
    workspace = get_workspace(workspace_id)
    if workspace is None:
        raise TaskEngineError(f"Unknown workspace: {workspace_id}")
    return workspace
