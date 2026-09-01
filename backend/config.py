"""Runtime configuration with YAML defaults and explicit environment overrides."""

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
SETTINGS_FILE = ROOT / "config" / "settings.yaml"
load_dotenv(ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    assistant_name: str
    personality_file: Path
    memory_file: Path
    default_provider: str
    default_model: str
    ollama_base_url: str
    groq_api_key: str
    openrouter_api_key: str
    host: str
    port: int
    max_agent_steps: int
    features: dict[str, bool]


def _yaml_settings() -> dict[str, Any]:
    data = yaml.safe_load(SETTINGS_FILE.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise TypeError("config/settings.yaml must contain a mapping")
    return data


def _get_env(name: str, default: str) -> str:
    return os.getenv(f"NEXUS_{name}", default)


@lru_cache
def get_settings() -> Settings:
    data = _yaml_settings()
    assistant = data.get("assistant", {})
    models = data.get("models", {})
    limits = data.get("limits", {})
    features = data.get("features", {})

    return Settings(
        assistant_name=str(assistant.get("name", "NEXUS")),
        personality_file=ROOT / str(assistant.get("personality_file", "config/personality.md")),
        memory_file=ROOT / str(assistant.get("memory_file", "config/memory.md")),
        default_provider=_get_env(
            "DEFAULT_PROVIDER", str(models.get("default_provider", "ollama"))
        ).lower(),
        default_model=_get_env("DEFAULT_MODEL", str(models.get("default_model", "llama3.2"))),
        ollama_base_url=_get_env("OLLAMA_BASE_URL", "http://localhost:11434"),
        groq_api_key=_get_env("GROQ_API_KEY", ""),
        openrouter_api_key=_get_env("OPENROUTER_API_KEY", ""),
        host=_get_env("HOST", "127.0.0.1"),
        port=int(_get_env("PORT", "8000")),
        max_agent_steps=int(_get_env("MAX_AGENT_STEPS", str(limits.get("max_agent_steps", 5)))),
        features={name: bool(enabled) for name, enabled in features.items()},
    )
