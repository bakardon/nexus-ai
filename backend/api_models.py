from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    task: str | None = None
    workspace_id: str | None = None
    provider: str | None = None
    model: str | None = None
    use_tools: bool = True


class WorkspaceRequest(BaseModel):
    objective: str = Field(min_length=1)
    task_type: str = "general"


class MemoryRequest(BaseModel):
    entry: str = Field(min_length=1)


class ApprovalRequest(BaseModel):
    approved: bool
