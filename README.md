# NEXUS

**A personal workbench for getting things done.**

NEXUS is a general-purpose personal intelligence and task-execution workspace. Instead of starting a new chat for every problem, you give NEXUS an objective and it creates a persistent workspace around it — with a plan, relevant context, tools, results, and task history.

It is designed to help a person **research, think, learn, create, analyze, organize, and eventually take approved actions** from one clean interface.

> **Prototype:** NEXUS is an early local-first prototype. The current release demonstrates persistent task workspaces, scoped memory, local Ollama execution, capability controls, and a customer-oriented workspace UI. External write actions are not yet production-ready.

## Why NEXUS?

Most AI products are built around a conversation: ask a question, receive an answer, start again.

NEXUS is built around **work**.

A customer should be able to say:

- “Research whether opening a convenience store in Islamabad makes sense.”
- “Help me prepare for this interview and keep track of what I still need to learn.”
- “Compare these three business ideas and tell me which deserves more investigation.”
- “Analyze these files and turn the findings into a report.”
- “Keep working on this project from where we left off.”

NEXUS turns those requests into persistent, understandable workspaces rather than disposable chat sessions.

## Customer Experience

```text
Tell NEXUS what you want to accomplish
                 ↓
          NEXUS creates a workspace
                 ↓
       Understands the objective
                 ↓
       Builds a practical plan
                 ↓
     Uses relevant tools + context
                 ↓
          Produces useful work
                 ↓
       Shows what it actually did
                 ↓
        Keeps the useful context
                 ↓
       Continue whenever you want
```

The customer should care about the **objective and outcome**, not agents, chains, prompts, tokens, or framework internals.

## What the Prototype Demonstrates

- Persistent task/workspace creation
- Separate task-specific memory
- User-editable personality and durable memory
- Local model execution through Ollama
- Capability availability checks
- Calculator and web-search tooling
- Execution status and task events
- Conservative approval handling for side-effecting tasks
- Explicit `unverified` result state when NEXUS has not independently verified an answer
- Clean three-panel workspace UI

## Interface

The prototype uses a focused workspace layout:

```text
┌────────────────┬────────────────────────────────┬─────────────────┐
│   WORKSPACES   │          ACTIVE TASK           │     CONTEXT     │
│                │                                │                 │
│   + New task   │  Objective                     │  Memory         │
│                │                                │                 │
│   Research     │  Plan                          │  Sources        │
│   Interview    │  Execution                     │  Files          │
│   Business     │                                │  Artifacts      │
│                │  Result                        │                 │
│   Settings     │  [ Tell NEXUS what to do ]    │                 │
└────────────────┴────────────────────────────────┴─────────────────┘
```

The design deliberately avoids looking like a developer console or generic chatbot. Framework logs belong behind the experience.

## Product Principles

1. **Outcome over conversation.** NEXUS exists to help accomplish objectives, not maximize chat length.
2. **Useful before impressive.** Every feature should solve a real customer problem.
3. **Trust over theatrics.** Never claim something happened when it did not.
4. **Visible progress.** Customers should understand what NEXUS is doing and why.
5. **Customer control.** External or consequential actions require clear approval.
6. **Context without clutter.** Keep useful information attached to the relevant task.
7. **Local-first and affordable.** The core experience should work without requiring a paid AI subscription.
8. **Provider independence.** Models and APIs are replaceable implementation details.
9. **Simple customization.** Personality and durable memory should be editable without programming.
10. **Real capabilities only.** If NEXUS cannot perform an action, it should say so clearly.

## Product Roadmap

### Prototype — current

- [x] Persistent workspaces
- [x] Task-scoped memory foundation
- [x] Local Ollama provider
- [x] Capability registry
- [x] Approval-aware execution foundation
- [x] Execution verification state
- [x] Customer-oriented workspace UI
- [ ] Real-time execution timeline
- [ ] Fully populated memory/sources/files/artifacts panels

### Next

- Reliable end-to-end task execution with real Ollama models
- Workspace conversation/history
- Live tool and execution events
- Better capability selection based on the actual objective
- Search/source cards with evidence
- Memory inspection and editing
- File upload and analysis
- Artifact generation and preview
- Approval experience for consequential actions

### Later

- Coding and repository workflows
- Documents and presentations
- Browser-based workflows
- Email/calendar integrations
- GitHub workflows
- Social publishing and other external services
- Multi-step background jobs
- Additional free/local model providers

External services are capabilities, not the product itself. NEXUS should never become architecturally dependent on one service or model provider.

## Trust & Safety

NEXUS distinguishes between **producing information** and **taking action**.

Read/analyze operations can generally be performed automatically when the required capability is available. Meaningful external/write operations — publishing, sending, deleting, submitting, changing external systems, and similar actions — require explicit approval under the current policy.

A model response is not automatically treated as verified truth. The prototype can report that execution succeeded while still marking the result `unverified` when independent verification has not occurred.

## Architecture

The implementation is intentionally modular:

- **FastAPI** — backend API
- **LangGraph / LangChain Core** — orchestration and tool-calling foundation
- **Ollama** — local/free inference path
- **OpenAI-compatible providers** — replaceable hosted path
- **DDGS** — web-search capability
- **Markdown/YAML** — customer-editable personality, memory, settings, and task profiles
- **Task Workspaces** — persistent objective, memory, plan, events, artifacts, and state
- **Capability Registry** — inventory of what NEXUS can actually do
- **Permission Policy** — risk levels and approval requirements

### Workspace model

Each task gets its own workspace containing its objective, plan, task memory, events, artifacts, and execution state. Core/durable memory remains separate and is only made relevant to a task when appropriate.

## Customer-Editable Configuration

```text
config/
├── personality.md       # How NEXUS communicates
├── memory.md            # Durable user context
├── settings.yaml        # Models, features, limits
└── tasks.yaml           # Task profiles and capability requirements
```

A normal personality or memory change should not require editing Python code.

Runtime workspaces live under `data/` by default and can be relocated with `NEXUS_DATA_DIR`.

## Local Prototype Setup

### Requirements

- Python 3.11+
- Ollama
- Node.js 20+ recommended for the frontend

### Backend

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
uvicorn backend.main:app --reload
```

Install the model configured in `config/settings.yaml` and make sure Ollama is running.

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

The Vite server will print the local URL. The frontend expects the API at `http://127.0.0.1:8000` by default; set `VITE_API_BASE` if required.

## Quality Checks

```powershell
pytest -q
ruff check backend tests
ruff format --check backend tests
python -m compileall backend
pip check
```

For UI changes:

```powershell
cd frontend
npm run build
```

Do not claim a capability works without testing its end-to-end path. External services should have a local/mock test path where practical.

## Development Rules

1. Read this README and `config/` before changing architecture.
2. Prefer mature existing open-source projects and libraries instead of rebuilding standard infrastructure.
3. Evaluate dependencies for maintenance, licensing, reliability, security, and actual necessity.
4. Keep modules small and testable.
5. Never commit secrets or API keys.
6. Keep the product understandable to a non-developer.
7. Prefer customer-facing concepts over framework terminology.
8. Preserve provider and capability boundaries.
9. Keep task memory isolated.
10. Fix underlying behavior rather than adding superficial UI workarounds.

## Free / Local Model Strategy

NEXUS should prefer local and genuinely free inference. Candidate models and providers must be evaluated for availability, licensing, context length, tool-calling support, hardware requirements, latency, rate limits, and reliability.

Repositories such as `12britz/awesome-free-models` can be used as discovery references, but are not product dependencies.

## Repository

NEXUS is currently an experimental prototype. The long-term goal is a trustworthy personal workbench that can take a broad range of real-world objectives from idea to useful outcome while keeping the customer in control.
