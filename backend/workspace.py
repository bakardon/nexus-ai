from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass
class TaskWorkspace:
    id: str
    objective: str
    task_type: str
    created_at: str
    memory: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    status: str = "active"


_WORKSPACES: dict[str, TaskWorkspace] = {}


def create_workspace(objective: str, task_type: str = "general") -> TaskWorkspace:
    workspace = TaskWorkspace(
        id=str(uuid4()),
        objective=objective,
        task_type=task_type,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    _WORKSPACES[workspace.id] = workspace
    return workspace


def get_workspace(workspace_id: str) -> TaskWorkspace | None:
    return _WORKSPACES.get(workspace_id)
