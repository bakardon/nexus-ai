from dataclasses import dataclass

from .permissions import TOOL_PERMISSIONS


@dataclass(frozen=True)
class Capability:
    name: str
    description: str
    available: bool
    risk: str
    requires_approval: bool


CAPABILITIES = {
    "web_search": Capability("web_search", "Search the public web", True, "read", False),
    "calculator": Capability("calculator", "Perform arithmetic", True, "read", False),
    "read_file": Capability("read_file", "Read a user-provided file", False, "read", False),
    "write_file": Capability("write_file", "Create or modify a file", False, "write", True),
    "publish": Capability("publish", "Publish content to an external service", False, "external", True),
    "send_message": Capability("send_message", "Send a message externally", False, "external", True),
}


def available_capabilities() -> list[Capability]:
    return [capability for capability in CAPABILITIES.values() if capability.available]


def capability_status(name: str) -> Capability | None:
    return CAPABILITIES.get(name)
