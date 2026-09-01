from dataclasses import dataclass


@dataclass(frozen=True)
class VerificationResult:
    execution_ok: bool
    output_ok: bool
    verified: bool
    status: str
    note: str


def inspect_output(response: str, tool_events: list[dict]) -> VerificationResult:
    """Perform deterministic integrity checks without pretending to fact-check the model."""
    text = response.strip()
    failed_tools = [event for event in tool_events if event.get("status") == "failed"]

    if failed_tools:
        return VerificationResult(
            execution_ok=False,
            output_ok=bool(text),
            verified=False,
            status="failed",
            note="One or more requested tools failed during execution.",
        )

    if not text:
        return VerificationResult(
            execution_ok=True,
            output_ok=False,
            verified=False,
            status="unverified",
            note="The model returned an empty response.",
        )

    return VerificationResult(
        execution_ok=True,
        output_ok=True,
        verified=False,
        status="unverified",
        note="Execution integrity passed, but model claims and facts were not independently verified.",
    )
