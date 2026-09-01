# NEXUS AI

A modular personal intelligence system built around free/local LLM inference, tools, retrieval, memory, and agent workflows.

## Architecture

- **Open WebUI** — user interface and model-facing workspace
- **FastAPI** — NEXUS backend API
- **LangGraph** — agent orchestration and tool workflows
- **Ollama** — local inference fallback
- **OpenAI-compatible providers** — interchangeable hosted models

## MVP

The first milestone is intentionally small: expose a clean API that can route a user request to an LLM provider and return a response. Research, reasoning, learning, memory, and RAG agents will be added incrementally.

## Principles

1. Prefer proven open-source components over rebuilding infrastructure.
2. Keep model providers interchangeable.
3. Keep the UI simple; hide orchestration complexity.
4. Use tools and evidence for insight-heavy tasks instead of relying on prompts alone.
5. Build evaluation into the system as capabilities grow.

## Project Status

🚧 MVP — initial scaffolding
