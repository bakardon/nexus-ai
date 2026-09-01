import os
import re
from pathlib import Path

from .config import get_settings
from .task_registry import ROOT


def task_memory_root() -> Path:
    return Path(os.getenv("NEXUS_DATA_DIR", ROOT / "data")) / "task-memory"


def _terms(text: str) -> set[str]:
    ignored = {"about", "after", "and", "are", "for", "from", "into", "that", "the", "this", "with"}
    return {term for term in re.findall(r"[a-z0-9]{3,}", text.lower()) if term not in ignored}


def select_relevant_core_memory(query: str, core_memory: str | None = None) -> str:
    """Return only durable-memory sections that overlap the task's terms."""
    source = core_memory or get_settings().memory_file.read_text(encoding="utf-8")
    query_terms = _terms(query)
    sections = re.split(r"(?=^## )", source, flags=re.MULTILINE)
    selected = []
    for section in sections:
        if not section.startswith("## "):
            continue
        if query_terms.intersection(_terms(section)):
            selected.append(section.strip())
    return "\n\n".join(selected)


def load_task_memory(workspace_id: str) -> str:
    scoped = task_memory_root() / f"{workspace_id}.md"
    return scoped.read_text(encoding="utf-8") if scoped.exists() else ""


def load_memory(scope: str = "core", workspace_id: str | None = None, query: str = "") -> str:
    relevant_core = select_relevant_core_memory(query)
    if scope == "core":
        return relevant_core

    if scope == "task" and workspace_id:
        task_memory = load_task_memory(workspace_id)
        parts = [part for part in (relevant_core, task_memory) if part]
        return "\n\n## Task Memory\n".join(parts)

    return relevant_core


def build_memory_context(
    scope: str = "core",
    workspace_id: str | None = None,
    query: str = "",
    max_chars: int = 12000,
) -> str:
    return load_memory(scope, workspace_id, query)[:max_chars]


def append_task_memory(workspace_id: str, entry: str) -> None:
    entry = entry.strip()
    if not entry:
        return
    root = task_memory_root()
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{workspace_id}.md"
    with path.open("a", encoding="utf-8") as file:
        file.write(f"\n- {entry}\n")
