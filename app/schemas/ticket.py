"""
Ticket Pydantic schemas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator

from app.models.enums import TicketPriority, TicketStatus, TicketVisibility


class TicketBase(BaseModel):
    """Ticket 基礎 schema"""
    title: str = Field(..., min_length=1, max_length=200, description="工單標題")
    description: Optional[str] = Field(None, description="工單描述")
    priority: TicketPriority = Field(TicketPriority.MEDIUM, description="優先級")
    visibility: TicketVisibility = Field(TicketVisibility.INTERNAL, description="可見性")
    due_date: Optional[datetime] = Field(None, description="到期日期")
    custom_fields_data: Optional[Dict[str, Any]] = Field(None, description="自定義欄位資料")


class TicketCreate(TicketBase):
    """創建 Ticket 的 schema"""
    ticket_template_id: Optional[int] = Field(None, description="工單範本 ID")
    approval_template_id: Optional[int] = Field(None, description="簽核範本 ID")
    category_ids: Optional[List[int]] = Field(default_factory=list, description="分類 ID 列表")
    label_ids: Optional[List[int]] = Field(default_factory=list, description="標籤 ID 列表")
    assigned_to: Optional[int] = Field(None, description="指派給用戶 ID")

    @validator('category_ids', 'label_ids')
    def validate_ids(cls, v):
        """驗證 ID 列表"""
        if v is None:
            return []
        return list(set(v))  # 去重


class TicketUpdate(BaseModel):
    """更新 Ticket 的 schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="工單標題")
    description: Optional[str] = Field(None, description="工單描述")
    priority: Optional[TicketPriority] = Field(None, description="優先級")
    visibility: Optional[TicketVisibility] = Field(None, description="可見性")
    due_date: Optional[datetime] = Field(None, description="到期日期")
    custom_fields_data: Optional[Dict[str, Any]] = Field(None, description="自定義欄位資料")
    category_ids: Optional[List[int]] = Field(None, description="分類 ID 列表")
    label_ids: Optional[List[int]] = Field(None, description="標籤 ID 列表")
    assigned_to: Optional[int] = Field(None, description="指派給用戶 ID")

    @validator('category_ids', 'label_ids')
    def validate_ids(cls, v):
        """驗證 ID 列表"""
        if v is None:
            return None
        return list(set(v))  # 去重


class TicketStatusUpdate(BaseModel):
    """狀態更新 schema"""
    status: TicketStatus = Field(..., description="新狀態")
    comment: Optional[str] = Field(None, description="狀態變更備註")


class CategorySummary(BaseModel):
    """分類摘要"""
    id: int
    name: str
    color: Optional[str] = None

    class Config:
        from_attributes = True


class LabelSummary(BaseModel):
    """標籤摘要"""
    id: int
    name: str
    color: Optional[str] = None

    class Config:
        from_attributes = True


class TicketResponse(TicketBase):
    """Ticket 響應 schema"""
    id: int
    ticket_no: str
    status: TicketStatus
    ticket_template_id: Optional[int]
    approval_template_id: Optional[int]
    assigned_to: Optional[int]
    created_by: int
    created_at: datetime
    updated_by: Optional[int]
    updated_at: Optional[datetime]
    categories: List[CategorySummary] = []
    labels: List[LabelSummary] = []

    class Config:
        from_attributes = True


class TicketListItem(BaseModel):
    """Ticket 列表項目 schema（簡化版）"""
    id: int
    ticket_no: str
    title: str
    status: TicketStatus
    priority: TicketPriority
    visibility: TicketVisibility
    assigned_to: Optional[int]
    due_date: Optional[datetime]
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime]
    categories: List[CategorySummary] = []
    labels: List[LabelSummary] = []

    class Config:
        from_attributes = True


class TicketSearchParams(BaseModel):
    """Ticket 搜尋參數"""
    title: Optional[str] = Field(None, description="標題關鍵字")
    status: Optional[List[TicketStatus]] = Field(None, description="狀態列表")
    priority: Optional[List[TicketPriority]] = Field(None, description="優先級列表")
    visibility: Optional[TicketVisibility] = Field(None, description="可見性")
    assigned_to: Optional[int] = Field(None, description="指派給用戶 ID")
    created_by: Optional[int] = Field(None, description="創建者用戶 ID")
    category_ids: Optional[List[int]] = Field(None, description="分類 ID 列表")
    label_ids: Optional[List[int]] = Field(None, description="標籤 ID 列表")
    due_date_from: Optional[datetime] = Field(None, description="到期日期開始")
    due_date_to: Optional[datetime] = Field(None, description="到期日期結束")
    created_from: Optional[datetime] = Field(None, description="創建日期開始")
    created_to: Optional[datetime] = Field(None, description="創建日期結束")


class TicketListResponse(BaseModel):
    """Ticket 列表響應"""
    items: List[TicketListItem]
    total: int
    page: int
    size: int
    total_pages: int


class TicketStatsResponse(BaseModel):
    """Ticket 統計響應"""
    total: int
    by_status: Dict[str, int]
    by_priority: Dict[str, int]
    overdue: int
    assigned_to_me: int
    created_by_me: int