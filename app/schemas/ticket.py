from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.models.enums import TicketPriority, TicketStatus, TicketVisibility
from app.models.ticket import Ticket
from app.schemas.category import CategoryRead
from app.schemas.label import LabelRead
from app.schemas.pagination import PaginationQuery

# 查詢參數 schema


class TicketQueryParams(PaginationQuery):
    # Filters flattened for query parameters
    status: TicketStatus | None = Field(None, description="工單狀態")
    priority: TicketPriority | None = Field(None, description="優先順序")
    visibility: TicketVisibility | None = Field(None, description="可見性")
    assigned_to: int | None = Field(None, description="指派對象")
    created_by: int | None = Field(None, description="建立者")
    ticket_template_id: int | None = Field(None, description="工單模板")
    approval_template_id: int | None = Field(None, description="簽核模板")

    @classmethod
    def _normalize_sort_order(cls, v: str | None):
        if v is None:
            return "desc"
        low = v.lower()
        return "asc" if low == "asc" else "desc"

    _norm_sort_order = field_validator("sort_order", mode="before", check_fields=False)(_normalize_sort_order)

    @classmethod
    def _validate_sort_by(cls, v: str | None):
        if not v:
            return "created_at"
        allowed = {c.key for c in Ticket.__table__.columns}
        return v if v in allowed else "created_at"

    _validate_sort_by_field = field_validator("sort_by", mode="before", check_fields=False)(_validate_sort_by)


# ...existing code...


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
    """Ticket 更新 Schema - 不繼承 TicketBase 因為需要所有欄位都是可選的

    雖然理論上可以覆寫欄位為可選，但 Pydantic 的類型系統不允許這樣做，
    所以選擇獨立定義以保持清晰和避免類型錯誤。
    """

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
    categories: list[CategoryRead] | None = None  # CategoryRead 的資料
    labels: list[LabelRead] | None = None  # LabelRead 的資料

    class Config:
        from_attributes = True


# 狀態變更專用的 Schema
class TicketStatusUpdate(BaseModel):
    status: TicketStatus
    reason: str | None = Field(None, max_length=500, description="狀態變更原因")


# 特定欄位更新的請求模型
class TicketTitleUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)


class TicketDescriptionUpdate(BaseModel):
    description: str | None = None


class TicketAssigneeUpdate(BaseModel):
    assigned_to: int | None = None


class TicketLabelsUpdate(BaseModel):
    label_ids: list[int]
