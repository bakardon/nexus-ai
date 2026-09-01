from dataclasses import dataclass


@dataclass(frozen=True)
class TaskIntent:
    task_type: str
    objective: str
    needs_web: bool
    needs_calculation: bool
    is_action: bool


def infer_intent(message: str) -> TaskIntent:
    text = message.lower()
    research_words = ("research", "find out", "compare", "latest", "look up", "investigate")
    calculation_words = ("calculate", "how much", "percentage", "roi", "cost", "profit")
    action_words = ("post", "send", "publish", "create", "delete", "update", "upload", "submit")

    needs_web = any(word in text for word in research_words)
    needs_calculation = any(word in text for word in calculation_words)
    is_action = any(word in text for word in action_words)

    if is_action:
        # Generic requested actions are handled conservatively by the content
        # profile, which requires approval before write/external execution.
        task_type = "content"
    elif needs_web:
        task_type = "research"
    elif any(word in text for word in ("should i", "decide", "decision", "worth it")):
        task_type = "decision"
    else:
        task_type = "general"

    return TaskIntent(
        task_type=task_type,
        objective=message.strip(),
        needs_web=needs_web,
        needs_calculation=needs_calculation,
        is_action=is_action,
    )
