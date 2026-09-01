# NEXUS AI

A modular personal intelligence and task-execution system built around free/local LLM inference, tools, retrieval, scoped memory, verification, and agent workflows.

## Vision

NEXUS is not intended to be a single-purpose chatbot. The user should be able to give it a natural-language objective and have NEXUS create a task workspace, understand the task, select available capabilities, use relevant memory, plan the work, execute tools, verify results, and present the outcome cleanly.

Examples include research, decision support, learning, coding, document creation, business analysis, project work, and eventually controlled interaction with external services. Specific services such as Instagram are examples of future capabilities, not core architecture.

## Current Architecture

- **FastAPI** — backend API
- **LangGraph / LangChain Core** — orchestration and tool-calling foundation
- **Ollama** — local/free inference path
- **OpenAI-compatible providers** — interchangeable hosted model path
- **DDGS** — web-search capability
- **Human-readable Markdown/YAML** — personality, core memory, task profiles, settings
- **Task Workspaces** — isolate objective, task memory, artifacts, status, and future execution state
- **Capability Registry** — central inventory of what NEXUS can actually do
- **Permission Policy** — read/write/external risk levels and approval requirements

## Non-Negotiable Priorities

1. **Actually work before looking impressive.** Do not add features without testing their integration.
2. **Free/local first.** Prefer open-source software and free APIs. Never make a paid provider mandatory for core functionality.
3. **Provider independence.** Model/API providers must be replaceable. A free provider disappearing must not destroy the architecture.
4. **No hallucinated capabilities.** If a tool is unavailable, NEXUS must say so rather than claiming the task was completed.
5. **Verify actions.** A successful API call is not automatically proof that the requested outcome happened. Verify state whenever possible.
6. **Human approval for side effects.** Publishing, sending, deleting, submitting, modifying external systems, or other meaningful write/external actions require explicit approval unless the user deliberately changes the policy.
7. **Task-scoped memory.** When the user assigns a task, create/select a workspace and allocate relevant memory to that task. Do not dump the user's entire memory into every prompt.
8. **Core memory remains user-controlled.** Personality and durable user context must be easy to inspect and edit without touching Python.
9. **Use existing projects intelligently.** Prefer mature GitHub projects and proven libraries over rebuilding standard infrastructure, but evaluate maintenance, licensing, reliability, security, and whether a dependency is genuinely needed.
10. **Clean UI.** The interface should feel like a focused task workspace, not a developer console or generic chatbot.

## User-Editable Configuration

```text
config/
├── personality.md       # How NEXUS behaves and communicates
├── memory.md            # User-controlled durable/core memory
├── settings.yaml        # Models, features, limits
├── tasks.yaml           # Optional task profiles and tool requirements
└── memory/
    └── tasks/           # Workspace-specific memory created during tasks
```

Normal personality, memory, and behavior changes should not require editing application code.

## Target Task Lifecycle

```text
Natural-language objective
        ↓
Intent / task understanding
        ↓
Create or resume workspace
        ↓
Select relevant core + task memory
        ↓
Discover required capabilities
        ↓
Check availability + permissions
        ↓
Create execution plan
        ↓
Execute tools / model reasoning
        ↓
Verify important outputs
        ↓
Request approval for side effects
        ↓
Execute approved external action
        ↓
Present result + evidence/artifacts
        ↓
Save only useful task memory
```

## Target UI

Inspired by the supplied product-demo reference, the UI should be a clean three-area task workspace:

- **Task sidebar** — new, active, and previous workspaces
- **Main workspace** — objective, plan, execution state, conversation, and results
- **Context panel** — relevant memory, sources, files, and artifacts
- **Approval bar/modal** — unmistakable confirmation for external/write actions

Tool activity should appear as compact human-readable states rather than raw framework logs.

## Capability Model

Capabilities are generic and should not be hard-coded around one service:

```text
READ
- web search
- read files
- inspect data

COMPUTE
- calculator
- Python/data analysis

CREATE
- documents
- code
- images/content

EXTERNAL
- GitHub
- email
- calendar
- social platforms
- browser/web actions
```

New capabilities should be implemented as adapters behind the capability registry and permission system.

## Model Strategy

Use a provider abstraction so NEXUS can choose among:

- local Ollama models
- genuinely free hosted APIs
- other OpenAI-compatible providers when available

Free-model catalogues such as `12britz/awesome-free-models` may be used to discover candidates, but they are references, not dependencies. Before adopting a provider/model, check current availability, limits, authentication requirements, license, latency, context length, tool-calling support, and reliability.

## Development Rules for Codex

When continuing development:

1. Read this README and the files under `config/` before making architectural changes.
2. Inspect the existing implementation before adding another framework or agent abstraction.
3. Prefer small, testable modules.
4. Keep secrets in `.env`; never place API keys in Markdown/YAML memory or source control.
5. Add tests for important behavior, especially routing, memory isolation, permissions, tool execution, and verification.
6. Do not claim a capability is implemented until its end-to-end path works.
7. When a feature depends on an external service, provide a local/mock test path.
8. Keep user-facing configuration simple and documented.
9. Preserve backward compatibility where practical.
10. If an external dependency is unreliable or paid, find a free/local alternative before making it core.

## Project Status

🚧 Early architecture / task-engine phase. The next priority is to make the task lifecycle reliable end-to-end, then build the polished UI on top of it.
