from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import AttachmentUsageType


class AttachmentBase(BaseModel):
    related_type: str | None = Field(None, description="關聯類型，如 'tickets', 'ticket_notes'")
    related_id: int | None = Field(None, description="關聯資源的 ID")
    ticket_id: int | None = Field(None, description="Ticket ID (用於快速查找)")
    usage_type: AttachmentUsageType = Field(AttachmentUsageType.GENERAL, description="附件用途類型")
    file_name: str = Field(..., min_length=1, max_length=255, description="原始文件名")
    storage_path: str = Field(..., description="存儲路徑")
    file_size: int = Field(..., gt=0, description="文件大小 (字節)")
    mime_type: str = Field(..., max_length=100, description="MIME 類型")
    storage_provider: str = Field("local", description="存儲提供商")
    description: str | None = Field(None, description="附件描述")


class AttachmentUpdate(BaseModel):
    """更新附件時的請求數據"""

    related_type: str | None = Field(None, description="關聯類型，如 'tickets', 'ticket_notes'")
    related_id: int | None = Field(None, description="關聯資源的 ID")
    ticket_id: int | None = Field(None, description="Ticket ID (用於快速查找)")
    description: str | None = Field(None, description="附件描述")


class AttachmentRead(AttachmentBase):
    """附件響應數據"""

    id: int
    created_by: int
    created_at: datetime
    updated_by: int | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class AttachmentUploadResponse(BaseModel):
    """上傳附件後的響應"""

    attachment: AttachmentRead
    upload_url: str | None = Field(None, description="文件訪問 URL")


class MultipleAttachmentUploadResponse(BaseModel):
    """批量上傳附件後的響應"""

    attachments: list[AttachmentRead]
    total_uploaded: int


class AttachmentListResponse(BaseModel):
    """附件列表響應"""

    attachments: list[AttachmentRead]
    total: int


# Rich Text Image 相關的 Schemas
class AttachmentListRequest(BaseModel):
    """附件列表請求"""

    related_type: str = Field(..., description="關聯類型，如 'tickets', 'ticket_notes'")
    related_id: int = Field(..., description="關聯資源的 ID")
    usage_type: str | None = Field(None, description="過濾附件用途類型")


class RichTextImageUploadResponse(BaseModel):
    """Rich Text 圖片上傳響應"""

    attachment: AttachmentRead
    attachment_id: int = Field(..., description="附件 ID，用於下載圖片")
    markdown_syntax: str = Field(..., description="Markdown 語法")


class LinkAttachmentsRequest(BaseModel):
    """關聯附件請求"""

    attachment_ids: list[int] = Field(..., description="要關聯的附件 ID 列表")
    related_type: str = Field(..., description="關聯類型，如 'tickets', 'ticket_notes'")
    related_id: int = Field(..., description="關聯資源的 ID")


class LinkAttachmentsResponse(BaseModel):
    """關聯附件響應"""

    linked_attachments: list[AttachmentRead]
    total_linked: int


class UnifiedUploadRequest(BaseModel):
    """統一的上傳附件請求"""

    related_type: str | None = Field(None, description="關聯類型，如 'tickets', 'ticket_notes'")
    related_id: int | None = Field(None, description="關聯資源的 ID")
    usage_type: str = Field("general", description="附件用途類型")
    description: str | None = Field(None, description="附件描述")
    alt_text: str | None = Field(None, description="圖片替代文字（富文本圖片使用）")
    link_to_resource: bool = Field(True, description="是否立即關聯到資源，false表示預上傳")
