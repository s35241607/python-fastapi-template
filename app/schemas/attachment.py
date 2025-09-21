"""
檔案附件相關的 Pydantic schemas
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AttachmentBase(BaseModel):
    """附件基礎 schema"""
    file_name: str = Field(..., description="檔案名稱")
    description: Optional[str] = Field(None, description="檔案描述")
    usage_type: str = Field(default="attachment", description="檔案用途 (attachment/inline_image)")


class AttachmentCreate(AttachmentBase):
    """建立附件 schema"""
    pass


class AttachmentUpdate(BaseModel):
    """更新附件 schema"""
    file_name: Optional[str] = None
    description: Optional[str] = None


class Attachment(AttachmentBase):
    """附件回應 schema"""
    id: int
    ticket_id: Optional[int] = None
    file_path: str
    bucket_name: str
    file_size: int
    mime_type: str
    is_image: bool
    image_width: Optional[int] = None
    image_height: Optional[int] = None
    status: str
    file_url: Optional[str] = None
    url_expires_at: Optional[datetime] = None
    created_by: int
    created_at: datetime
    updated_by: Optional[int] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FileUploadResponse(BaseModel):
    """檔案上傳回應 schema"""
    success: bool
    message: str
    attachment: Optional[Attachment] = None
    upload_url: Optional[str] = None  # 如果需要分段上傳


class FileListResponse(BaseModel):
    """檔案列表回應 schema"""
    attachments: list[Attachment]
    total: int
    page: int
    page_size: int


class ImageUploadResponse(BaseModel):
    """圖片上傳回應 schema (用於富文本編輯器)"""
    success: bool
    message: str
    image_url: Optional[str] = None
    image_id: Optional[int] = None
    image_info: Optional[dict] = None


class FileUrlResponse(BaseModel):
    """檔案 URL 回應 schema"""
    file_url: str
    expires_at: datetime
    file_name: str
    file_size: int
    mime_type: str