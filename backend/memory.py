from pathlib import Path

from .task_registry import ROOT

CORE_MEMORY = ROOT / "config" / "memory.md"
TASK_MEMORY_ROOT = ROOT / "config" / "memory" / "tasks"


def load_memory(scope: str = "core", workspace_id: str | None = None) -> str:
    if scope == "core":
        return CORE_MEMORY.read_text(encoding="utf-8")

    if scope == "task" and workspace_id:
        scoped = TASK_MEMORY_ROOT / f"{workspace_id}.md"
        if scoped.exists():
            return scoped.read_text(encoding="utf-8")

    return "No task-specific memory has been recorded yet."


def build_memory_context(scope: str = "core", workspace_id: str | None = None, max_chars: int = 12000) -> str:
    return load_memory(scope, workspace_id)[:max_chars]


def append_task_memory(workspace_id: str, entry: str) -> None:
    TASK_MEMORY_ROOT.mkdir(parents=True, exist_ok=True)
    path = TASK_MEMORY_ROOT / f"{workspace_id}.md"
    with path.open("a", encoding="utf-8") as file:
        file.write(f"\n- {entry.strip()}\n")
