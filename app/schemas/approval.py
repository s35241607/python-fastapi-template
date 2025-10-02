from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import ApprovalProcessStatus, ApprovalProcessStepStatus


class ApprovalTemplateStepRead(BaseModel):
    id: int
    step_order: int
    role_id: int | None
    user_id: int | None
    is_mandatory: bool

    class Config:
        from_attributes = True


class ApprovalTemplateRead(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime | None
    steps: list[ApprovalTemplateStepRead] = []

    class Config:
        from_attributes = True


class ApprovalProcessStepRead(BaseModel):
    id: int
    approval_process_id: int
    step_order: int
    approver_id: int | None
    proxy_id: int | None
    status: ApprovalProcessStepStatus
    action_at: datetime | None
    comment: str | None
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class ApprovalProcessRead(BaseModel):
    id: int
    ticket_id: int
    approval_template_id: int | None
    status: ApprovalProcessStatus
    current_step: int
    created_at: datetime
    updated_at: datetime | None
    steps: list[ApprovalProcessStepRead] = []

    class Config:
        from_attributes = True


class ApprovalAction(BaseModel):
    comment: str | None = Field(None, max_length=500, description="簽核意見")