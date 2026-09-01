import asyncio
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage

from backend import agents
from backend.config import get_settings
from backend.main import app
from backend.memory import append_task_memory, build_memory_context, load_task_memory
from backend.permissions import ApprovalRequiredError, require_approval
from backend.providers import ProviderError
from backend.task_engine import start_task
from backend.task_intent import infer_intent
from backend.tools.calculator import calculator
from backend.workspace import get_workspace


@pytest.fixture(autouse=True)
def isolated_runtime_data(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setenv("NEXUS_DATA_DIR", str(tmp_path / "runtime"))
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_workspace_is_persistent_and_uses_requested_profile() -> None:
    workspace, plan = start_task("Compare local models", "research")

    restored = get_workspace(workspace.id)
    assert restored is not None
    assert restored.objective == "Compare local models"
    assert restored.task_type == "research"
    assert restored.status == "planned"
    assert restored.plan["steps"][0]["status"] == "completed"
    assert plan["capabilities"] == ["web_search", "calculator"]
    assert plan["memory_scope"] == "task"


def test_task_memory_is_isolated_between_workspaces() -> None:
    first, _ = start_task("First task", "research")
    second, _ = start_task("Second task", "research")
    append_task_memory(first.id, "Only the first workspace knows this.")

    assert "Only the first workspace knows this." in build_memory_context("task", first.id)
    assert "Only the first workspace knows this." not in build_memory_context("task", second.id)


def test_memory_context_selects_relevant_core_sections(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    core_memory = tmp_path / "memory.md"
    core_memory.write_text(
        "## Projects\nNEXUS is evaluating local language models.\n\n"
        "## Preferences\nThe user prefers concise answers.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "backend.memory.get_settings", lambda: SimpleNamespace(memory_file=core_memory)
    )
    workspace, _ = start_task("Evaluate local models", "research")
    append_task_memory(workspace.id, "Previous model benchmark: 8 GB RAM.")

    context = build_memory_context("task", workspace.id, "local models benchmark")
    assert "local language models" in context
    assert "concise answers" not in context
    assert "Previous model benchmark" in context


def test_action_intent_uses_conservative_profile() -> None:
    assert infer_intent("Publish this announcement").task_type == "content"
    _, plan = start_task("Publish this announcement")
    assert plan["requires_approval"] is True


def test_unknown_profile_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unknown task profile"):
        start_task("Do something", "unknown")


def test_write_and_external_capabilities_need_approval() -> None:
    with pytest.raises(ApprovalRequiredError):
        require_approval(["write_file"], approved=False)
    require_approval(["write_file"], approved=True)
    require_approval(["web_search"], approved=False)


@pytest.mark.parametrize(
    ("expression", "expected"),
    [("2 + 3 * 4", "14"), ("(12 - 5) / 2", "3.5")],
)
def test_calculator_evaluates_basic_arithmetic(expression: str, expected: str) -> None:
    assert calculator.invoke({"expression": expression}) == expected


@pytest.mark.parametrize("expression", ["__import__('os')", "2 ** 10001", "a + 1"])
def test_calculator_rejects_non_arithmetic_or_unbounded_input(expression: str) -> None:
    assert calculator.invoke({"expression": expression}).startswith(("Invalid", "Could not"))


def test_local_agent_records_tool_execution_with_a_fake_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeTool:
        name = "calculator"

        async def ainvoke(self, arguments: dict) -> str:
            assert arguments == {"expression": "2 + 2"}
            return "4"

    class FakeModel:
        def __init__(self) -> None:
            self.calls = 0

        async def ainvoke(self, _messages: list) -> AIMessage:
            self.calls += 1
            if self.calls == 1:
                return AIMessage(
                    content="",
                    tool_calls=[
                        {"name": "calculator", "args": {"expression": "2 + 2"}, "id": "call-1"}
                    ],
                )
            return AIMessage(content="The result is 4.")

    fake_model = FakeModel()
    profile = agents.get_task_profile("research")
    monkeypatch.setattr(
        agents,
        "build_local_agent",
        lambda _task: (fake_model, [FakeTool()], profile),
    )
    events: list[dict] = []

    response = asyncio.run(
        agents.run_local_agent(
            "Calculate 2 + 2",
            "research",
            memory_query="calculate",
            on_tool_event=events.append,
        )
    )
    assert response == "The result is 4."
    assert [event["status"] for event in events] == ["in_progress", "completed"]


def test_task_api_runs_a_workspace_with_its_own_identity(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_agent(message: str, task: str, workspace_id: str, **kwargs: object) -> str:
        callback = kwargs["on_tool_event"]
        await callback({"tool": "calculator", "status": "in_progress", "arguments": {}})
        await callback({"tool": "calculator", "status": "completed", "result": "4"})
        return f"{task}:{workspace_id}:{message}"

    monkeypatch.setattr("backend.main.run_local_agent", fake_agent)
    client = TestClient(app)

    started = client.post(
        "/api/tasks/start", json={"objective": "Research local models", "task_type": "research"}
    )
    assert started.status_code == 200
    workspace_id = started.json()["workspace"]["id"]

    executed = client.post(f"/api/tasks/{workspace_id}/run", json={"message": "Find options"})
    assert executed.status_code == 200
    assert executed.json()["workspace"]["status"] == "completed"
    assert executed.json()["workspace"]["verification_status"] == "unverified"
    assert executed.json()["workspace"]["plan"]["steps"][1]["status"] == "completed"
    assert any(
        event["message"] == "Tool calculator completed"
        for event in executed.json()["workspace"]["events"]
    )
    assert workspace_id in executed.json()["response"]


def test_task_api_blocks_an_approval_required_profile() -> None:
    client = TestClient(app)
    started = client.post(
        "/api/tasks/start", json={"objective": "Publish an update", "task_type": "content"}
    )
    workspace_id = started.json()["workspace"]["id"]

    response = client.post(f"/api/tasks/{workspace_id}/run", json={"message": "Publish it"})
    assert response.status_code == 409
    assert "explicit approval" in response.json()["detail"]
    assert client.get(f"/api/tasks/{workspace_id}").json()["status"] == "awaiting_approval"


def test_task_api_resumes_a_workspace_with_prior_task_memory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    async def fake_agent(message: str, _task: str, workspace_id: str, **_kwargs: object) -> str:
        calls.append(message)
        return f"response to {message} in {workspace_id}"

    monkeypatch.setattr("backend.main.run_local_agent", fake_agent)
    client = TestClient(app)
    workspace_id = client.post(
        "/api/tasks/start", json={"objective": "Research local models", "task_type": "research"}
    ).json()["workspace"]["id"]

    assert (
        client.post(f"/api/tasks/{workspace_id}/run", json={"message": "Find options"}).status_code
        == 200
    )
    resumed = client.post(
        f"/api/tasks/{workspace_id}/resume", json={"message": "Compare the options"}
    )

    assert resumed.status_code == 200
    assert calls == ["Find options", "Compare the options"]
    assert "response to Find options" in load_task_memory(workspace_id)
    assert len(resumed.json()["workspace"]["events"]) >= 5


def test_task_api_records_a_failed_local_model_run(monkeypatch: pytest.MonkeyPatch) -> None:
    async def unavailable_agent(*_args: object, **_kwargs: object) -> str:
        raise ProviderError("Ollama is unavailable")

    monkeypatch.setattr("backend.main.run_local_agent", unavailable_agent)
    client = TestClient(app)
    workspace_id = client.post(
        "/api/tasks/start", json={"objective": "Research local models", "task_type": "research"}
    ).json()["workspace"]["id"]

    response = client.post(f"/api/tasks/{workspace_id}/run", json={"message": "Find options"})
    assert response.status_code == 502
    workspace = client.get(f"/api/tasks/{workspace_id}").json()
    assert workspace["status"] == "failed"
    assert workspace["plan"]["steps"][1]["status"] == "failed"
