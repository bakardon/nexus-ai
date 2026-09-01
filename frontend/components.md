# NEXUS UI Components

## Layout

```text
┌──────────────┬──────────────────────────────┬─────────────────┐
│ TASKS        │ ACTIVE WORKSPACE             │ CONTEXT         │
│              │                              │                 │
│ + New task   │ objective                    │ Memory          │
│              │ plan                         │ Sources         │
│ Research     │ execution                    │ Files           │
│ Interview    │ conversation                 │ Artifacts       │
│ Business     │                              │                 │
│              │ [ message / command ]        │                 │
└──────────────┴──────────────────────────────┴─────────────────┘
```

## Rules

- New task starts from one natural-language objective.
- The task workspace owns task memory and artifacts.
- Show tool execution as compact status rows, not raw logs by default.
- Show sources beside research answers.
- Keep approval actions impossible to miss.
- Allow the user to inspect/edit memory before it becomes durable.
- Do not expose provider/model complexity unless requested.
