from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
TASKS_FILE = ROOT / "config" / "tasks.yaml"


@dataclass(frozen=True)
class TaskProfile:
    name: str
    description: str
    tools: tuple[str, ...]
    memory_scope: str
    approval_required: bool


def load_task_profiles() -> dict[str, TaskProfile]:
    data: dict[str, Any] = yaml.safe_load(TASKS_FILE.read_text(encoding="utf-8")) or {}
    profiles = data.get("profiles", {})
    return {
        name: TaskProfile(
            name=name,
            description=profile.get("description", ""),
            tools=tuple(profile.get("tools", [])),
            memory_scope=profile.get("memory_scope", "core"),
            approval_required=bool(profile.get("approval_required", True)),
        )
        for name, profile in profiles.items()
    }


def get_task_profile(name: str | None) -> TaskProfile:
    profiles = load_task_profiles()
    if "general" not in profiles:
        raise ValueError("config/tasks.yaml must define a general profile")
    if name is None:
        return profiles["general"]
    try:
        return profiles[name]
    except KeyError as exc:
        raise ValueError(f"Unknown task profile: {name}") from exc
