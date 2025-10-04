from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ApprovalProcessStatus, ApprovalProcessStepStatus


# =========================================
#  Approval Action
# =========================================
class ApprovalAction(BaseModel):
    comment: str | None = Field(None, max_length=500, description="簽核意見")


# =========================================
#  Approval Template Schemas
# =========================================
class ApprovalTemplateStepRead(BaseModel):
    id: int
    step_order: int
    role_id: int | None = None
    user_id: int | None = None

    model_config = ConfigDict(from_attributes=True)


class ApprovalTemplateRead(BaseModel):
    id: int
    name: str
    steps: list[ApprovalTemplateStepRead] = []

    model_config = ConfigDict(from_attributes=True)


# =========================================
#  Approval Process (Instance) Schemas
# =========================================
class ApprovalProcessStepRead(BaseModel):
    id: int
    step_order: int
    status: ApprovalProcessStepStatus
    approver_id: int | None = None
    proxy_id: int | None = None

    model_config = ConfigDict(from_attributes=True)


class ApprovalProcessRead(BaseModel):
    id: int
    status: ApprovalProcessStatus
    current_step: int | None = None
    steps: list[ApprovalProcessStepRead] = []

    model_config = ConfigDict(from_attributes=True)