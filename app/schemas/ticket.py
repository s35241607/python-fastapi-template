from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.enums import TicketPriority, TicketStatus, TicketVisibility
from app.schemas.category import CategoryRead
from app.schemas.label import LabelRead
from app.schemas.note import TicketNoteRead


class TicketBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    priority: TicketPriority = TicketPriority.MEDIUM
    visibility: TicketVisibility = TicketVisibility.INTERNAL
    due_date: datetime | None = None
    assigned_to: int | None = None


class TicketCreate(TicketBase):
    # Template 相關
    ticket_template_id: int | None = None
    approval_template_id: int | None = None
    custom_fields_data: dict[str, Any] | None = None

    # Category 和 Label 關聯 (使用 ID 列表)
    category_ids: list[int] = Field(default_factory=list[int])
    label_ids: list[int] = Field(default_factory=list[int])


class TicketUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    priority: TicketPriority | None = None
    visibility: TicketVisibility | None = None
    due_date: datetime | None = None
    assigned_to: int | None = None
    custom_fields_data: dict[str, Any] | None = None

    # Category 和 Label 更新 (可選)
    category_ids: list[int] | None = None
    label_ids: list[int] | None = None


class TicketRead(TicketBase):
    id: int
    ticket_no: str
    status: TicketStatus
    ticket_template_id: int | None = None
    approval_template_id: int | None = None
    custom_fields_data: dict[str, Any] | None = None

    # 建立/更新資訊
    created_by: int
    created_at: datetime
    updated_by: int | None = None
    updated_at: datetime | None = None

    # 關聯資料 (如果需要，可以包含完整的 category 和 label 物件)
    categories: list[CategoryRead] | None = None
    labels: list[LabelRead] | None = None
    notes: list[TicketNoteRead] | None = None

    class Config:
        from_attributes = True


# 狀態變更專用的 Schema
class TicketStatusUpdate(BaseModel):
    status: TicketStatus
    reason: str | None = Field(None, max_length=500, description="狀態變更原因")
