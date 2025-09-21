"""
檔案附件 API Router
提供檔案上傳、下載、管理等功能
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_user_id_from_jwt
from app.database import get_db
from app.repositories.attachment_repository import AttachmentRepository
from app.schemas.attachment import (
    Attachment,
    AttachmentUpdate,
    FileUploadResponse,
    FileUrlResponse,
    ImageUploadResponse,
)
from app.services.attachment_service import AttachmentService

router = APIRouter(dependencies=[Depends(get_user_id_from_jwt)])


async def get_attachment_service(db: AsyncSession = Depends(get_db)) -> AttachmentService:
    """取得附件服務"""
    attachment_repository = AttachmentRepository(db)
    return AttachmentService(attachment_repository)


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    ticket_id: Optional[int] = Form(None),
    usage_type: str = Form("attachment"),
    description: Optional[str] = Form(None),
    user_id: int = Depends(get_user_id_from_jwt),
    service: AttachmentService = Depends(get_attachment_service)
):
    """
    上傳檔案
    
    - **file**: 要上傳的檔案
    - **ticket_id**: 關聯的 ticket ID (可選)
    - **usage_type**: 使用類型 (attachment: 一般附件, inline_image: 內嵌圖片)
    - **description**: 檔案描述
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="檔案名稱不能為空")
    
    success, message, attachment = await service.upload_file(
        file=file,
        user_id=user_id,
        ticket_id=ticket_id,
        usage_type=usage_type,
        description=description
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return FileUploadResponse(
        success=True,
        message=message,
        attachment=attachment
    )


@router.post("/upload/image", response_model=ImageUploadResponse)
async def upload_image_for_richtext(
    file: UploadFile = File(...),
    ticket_id: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    user_id: int = Depends(get_user_id_from_jwt),
    service: AttachmentService = Depends(get_attachment_service)
):
    """
    上傳圖片 (專為富文本編輯器設計)
    
    - **file**: 要上傳的圖片檔案
    - **ticket_id**: 關聯的 ticket ID (可選)
    - **description**: 圖片描述
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="檔案名稱不能為空")
    
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只能上傳圖片檔案")
    
    success, message, attachment = await service.upload_file(
        file=file,
        user_id=user_id,
        ticket_id=ticket_id,
        usage_type="inline_image",
        description=description
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return ImageUploadResponse(
        success=True,
        message=message,
        image_url=attachment.file_url if attachment else None,
        image_id=attachment.id if attachment else None,
        image_info={
            "width": attachment.image_width,
            "height": attachment.image_height,
            "size": attachment.file_size,
            "type": attachment.mime_type
        } if attachment else None
    )


@router.get("/{attachment_id}", response_model=Attachment)
async def get_attachment(
    attachment_id: int,
    user_id: int = Depends(get_user_id_from_jwt),
    service: AttachmentService = Depends(get_attachment_service)
):
    """獲取附件資訊"""
    attachment = await service.get_attachment(attachment_id, user_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="附件不存在")
    
    return attachment


@router.get("/{attachment_id}/url", response_model=FileUrlResponse)
async def get_file_url(
    attachment_id: int,
    user_id: int = Depends(get_user_id_from_jwt),
    service: AttachmentService = Depends(get_attachment_service)
):
    """獲取檔案下載 URL"""
    attachment = await service.get_attachment(attachment_id, user_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="附件不存在")
    
    return FileUrlResponse(
        file_url=attachment.file_url,
        expires_at=attachment.url_expires_at,
        file_name=attachment.file_name,
        file_size=attachment.file_size,
        mime_type=attachment.mime_type
    )


@router.get("/{attachment_id}/download")
async def download_file(
    attachment_id: int,
    user_id: int = Depends(get_user_id_from_jwt),
    service: AttachmentService = Depends(get_attachment_service)
):
    """直接下載檔案"""
    success, file_content, filename, content_type = await service.download_file(
        attachment_id, user_id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="檔案不存在或下載失敗")
    
    def generate():
        yield file_content
    
    return StreamingResponse(
        generate(),
        media_type=content_type,
        headers={
            "Content-Disposition": f"attachment; filename=\"{filename}\"",
            "Content-Length": str(len(file_content))
        }
    )


@router.put("/{attachment_id}", response_model=Attachment)
async def update_attachment(
    attachment_id: int,
    attachment_update: AttachmentUpdate,
    user_id: int = Depends(get_user_id_from_jwt),
    service: AttachmentService = Depends(get_attachment_service)
):
    """更新附件資訊"""
    attachment = await service.update_attachment(
        attachment_id, attachment_update, user_id
    )
    
    if not attachment:
        raise HTTPException(status_code=404, detail="附件不存在")
    
    return attachment


@router.delete("/{attachment_id}")
async def delete_attachment(
    attachment_id: int,
    user_id: int = Depends(get_user_id_from_jwt),
    service: AttachmentService = Depends(get_attachment_service)
):
    """刪除附件"""
    success, message = await service.delete_attachment(attachment_id, user_id)
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"message": message}


@router.get("/ticket/{ticket_id}/attachments", response_model=List[Attachment])
async def get_ticket_attachments(
    ticket_id: int,
    usage_type: Optional[str] = None,
    user_id: int = Depends(get_user_id_from_jwt),
    service: AttachmentService = Depends(get_attachment_service)
):
    """
    獲取指定 ticket 的附件列表
    
    - **ticket_id**: Ticket ID
    - **usage_type**: 使用類型篩選 (attachment/inline_image)
    """
    attachments = await service.get_ticket_attachments(
        ticket_id=ticket_id,
        usage_type=usage_type
    )
    
    return attachments


@router.get("/ticket/{ticket_id}/images", response_model=List[Attachment])
async def get_ticket_images(
    ticket_id: int,
    user_id: int = Depends(get_user_id_from_jwt),
    service: AttachmentService = Depends(get_attachment_service)
):
    """獲取指定 ticket 的圖片列表 (用於富文本編輯器)"""
    images = await service.get_ticket_attachments(
        ticket_id=ticket_id,
        usage_type="inline_image"
    )
    
    return images