from pathlib import Path

from .task_registry import ROOT


CORE_MEMORY = ROOT / "config" / "memory.md"


def load_memory(scope: str = "core") -> str:
    """Load human-editable memory. Task-specific stores can be added later."""
    if scope == "core":
        return CORE_MEMORY.read_text(encoding="utf-8")

    scoped = ROOT / "config" / "memory" / f"{scope}.md"
    if scoped.exists():
        return scoped.read_text(encoding="utf-8")

    return "No task-specific memory has been configured."


def build_memory_context(scope: str = "core", max_chars: int = 12000) -> str:
    content = load_memory(scope)
    return content[:max_chars]
