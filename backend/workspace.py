import json
import os
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

WORKSPACE_STATUSES = {
    "planned",
    "in_progress",
    "awaiting_approval",
    "completed",
    "failed",
}
VERIFICATION_STATUSES = {"not_started", "unverified", "verified"}


@dataclass
class TaskWorkspace:
    id: str
    objective: str
    task_type: str
    created_at: str
    memory: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    plan: dict = field(default_factory=dict)
    events: list[dict] = field(default_factory=list)
    status: str = "planned"
    verification_status: str = "not_started"
    updated_at: str = ""


ROOT = Path(__file__).resolve().parents[1]


def workspace_root() -> Path:
    return Path(os.getenv("NEXUS_DATA_DIR", ROOT / "data")) / "workspaces"


def _path(workspace_id: str) -> Path:
    return workspace_root() / f"{workspace_id}.json"


def _save(workspace: TaskWorkspace) -> TaskWorkspace:
    root = workspace_root()
    root.mkdir(parents=True, exist_ok=True)
    workspace.updated_at = datetime.now(UTC).isoformat()
    destination = _path(workspace.id)
    temporary = destination.with_suffix(".tmp")
    temporary.write_text(json.dumps(asdict(workspace), indent=2), encoding="utf-8")
    temporary.replace(destination)
    return workspace


def create_workspace(objective: str, task_type: str = "general") -> TaskWorkspace:
    now = datetime.now(UTC).isoformat()
    workspace = TaskWorkspace(
        id=str(uuid4()),
        objective=objective,
        task_type=task_type,
        created_at=now,
        updated_at=now,
    )
    return _save(workspace)


def get_workspace(workspace_id: str) -> TaskWorkspace | None:
    path = _path(workspace_id)
    if not path.exists():
        return None
    return TaskWorkspace(**json.loads(path.read_text(encoding="utf-8")))


def list_workspaces() -> list[TaskWorkspace]:
    root = workspace_root()
    if not root.exists():
        return []
    workspaces: list[TaskWorkspace] = []
    for path in root.glob("*.json"):
        try:
            workspaces.append(TaskWorkspace(**json.loads(path.read_text(encoding="utf-8"))))
        except (OSError, json.JSONDecodeError, TypeError):
            continue
    return sorted(workspaces, key=lambda item: item.updated_at or item.created_at, reverse=True)


def save_workspace(workspace: TaskWorkspace) -> TaskWorkspace:
    return _save(workspace)


def record_event(workspace: TaskWorkspace, status: str, message: str, **details: object) -> None:
    if status not in WORKSPACE_STATUSES:
        raise ValueError(f"Unknown workspace status: {status}")
    workspace.events.append(
        {
            "at": datetime.now(UTC).isoformat(),
            "status": status,
            "message": message,
            "details": details,
        }
    )


def transition_workspace(
    workspace: TaskWorkspace, status: str, message: str, **details: object
) -> None:
    record_event(workspace, status, message, **details)
    workspace.status = status


def update_plan_step(workspace: TaskWorkspace, step_id: str, status: str, detail: str = "") -> None:
    for step in workspace.plan.get("steps", []):
        if step.get("id") == step_id:
            step["status"] = status
            if detail:
                step["detail"] = detail
            return
    raise ValueError(f"Unknown plan step: {step_id}")
