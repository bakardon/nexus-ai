from dataclasses import dataclass


@dataclass(frozen=True)
class ToolPermission:
    name: str
    risk: str  # read, write, external
    requires_approval: bool


TOOL_PERMISSIONS = {
    "web_search": ToolPermission("web_search", "read", False),
    "calculator": ToolPermission("calculator", "read", False),
    "read_file": ToolPermission("read_file", "read", False),
    "write_file": ToolPermission("write_file", "write", True),
    "publish": ToolPermission("publish", "external", True),
    "send_message": ToolPermission("send_message", "external", True),
}


def requires_approval(tool_names: list[str]) -> bool:
    return any(TOOL_PERMISSIONS.get(name, ToolPermission(name, "external", True)).requires_approval for name in tool_names)
