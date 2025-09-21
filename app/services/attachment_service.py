"""
附件服務
處理檔案上傳、下載、管理等業務邏輯
"""

import io
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from fastapi import UploadFile
from PIL import Image

from app.config import settings
from app.repositories.attachment_repository import AttachmentRepository
from app.schemas.attachment import Attachment, AttachmentCreate, AttachmentUpdate
from app.services.minio_service import minio_service


class AttachmentService:
    """附件服務"""

    def __init__(self, attachment_repository: AttachmentRepository):
        self.attachment_repository = attachment_repository
        self.minio_service = minio_service

    async def upload_file(
        self,
        file: UploadFile,
        user_id: int,
        ticket_id: Optional[int] = None,
        usage_type: str = "attachment",
        description: Optional[str] = None
    ) -> Tuple[bool, str, Optional[Attachment]]:
        """
        上傳檔案
        
        Args:
            file: 上傳的檔案
            user_id: 使用者 ID
            ticket_id: 關聯的 ticket ID (可選)
            usage_type: 使用類型 (attachment/inline_image)
            description: 檔案描述
            
        Returns:
            (success, message, attachment)
        """
        try:
            # 讀取檔案內容
            file_content = await file.read()
            
            # 判斷是否為圖片
            is_image = usage_type == "inline_image" or file.content_type.startswith("image/")
            
            # 上傳到 MinIO
            success, message, file_info = await self.minio_service.upload_file(
                file_content=file_content,
                filename=file.filename,
                is_image=is_image,
                folder=usage_type,
                metadata={
                    "user_id": str(user_id),
                    "ticket_id": str(ticket_id) if ticket_id else "",
                    "usage_type": usage_type,
                }
            )
            
            if not success:
                return False, message, None
            
            # 如果是圖片，獲取尺寸資訊
            image_width = None
            image_height = None
            if is_image:
                try:
                    img = Image.open(io.BytesIO(file_content))
                    image_width, image_height = img.size
                except Exception:
                    pass  # 如果無法讀取尺寸，繼續處理
            
            # 生成檔案 URL
            file_url = self.minio_service.get_file_url(
                bucket=file_info["bucket"],
                file_path=file_info["file_path"]
            )
            url_expires_at = datetime.now() + timedelta(seconds=settings.file_url_expiry)
            
            # 儲存到資料庫
            attachment = await self.attachment_repository.create_attachment(
                ticket_id=ticket_id,
                file_name=file.filename,
                file_path=file_info["file_path"],
                bucket_name=file_info["bucket"],
                file_size=file_info["file_size"],
                mime_type=file_info["mime_type"],
                is_image=is_image,
                usage_type=usage_type,
                user_id=user_id,
                description=description,
                image_width=image_width,
                image_height=image_height,
                file_url=file_url,
                url_expires_at=url_expires_at
            )
            
            # 轉換為 Pydantic 模型
            attachment_dict = {
                "id": attachment.id,
                "ticket_id": attachment.ticket_id,
                "file_name": attachment.file_name,
                "file_path": attachment.file_path,
                "bucket_name": attachment.bucket_name,
                "file_size": attachment.file_size,
                "mime_type": attachment.mime_type,
                "is_image": attachment.is_image,
                "image_width": attachment.image_width,
                "image_height": attachment.image_height,
                "usage_type": attachment.usage_type,
                "description": attachment.description,
                "status": attachment.status,
                "file_url": attachment.file_url,
                "url_expires_at": attachment.url_expires_at,
                "created_by": attachment.created_by,
                "created_at": attachment.created_at,
                "updated_by": attachment.updated_by,
                "updated_at": attachment.updated_at,
            }
            
            return True, "檔案上傳成功", Attachment(**attachment_dict)
            
        except Exception as e:
            return False, f"檔案上傳失敗: {str(e)}", None

    async def get_attachment(self, attachment_id: int, user_id: int) -> Optional[Attachment]:
        """獲取附件資訊"""
        attachment = await self.attachment_repository.get_by_id(attachment_id)
        if not attachment:
            return None
        
        # 檢查權限 (可以根據需求調整)
        # if attachment.created_by != user_id:
        #     return None
        
        # 檢查 URL 是否過期，如果過期則重新生成
        if attachment.url_expires_at and attachment.url_expires_at < datetime.now():
            file_url = self.minio_service.get_file_url(
                bucket=attachment.bucket_name,
                file_path=attachment.file_path
            )
            url_expires_at = datetime.now() + timedelta(seconds=settings.file_url_expiry)
            
            await self.attachment_repository.update_file_url(
                attachment_id=attachment_id,
                file_url=file_url,
                expires_at=url_expires_at,
                user_id=user_id
            )
            
            attachment.file_url = file_url
            attachment.url_expires_at = url_expires_at
        
        # 轉換為 Pydantic 模型
        attachment_dict = {
            "id": attachment.id,
            "ticket_id": attachment.ticket_id,
            "file_name": attachment.file_name,
            "file_path": attachment.file_path,
            "bucket_name": attachment.bucket_name,
            "file_size": attachment.file_size,
            "mime_type": attachment.mime_type,
            "is_image": attachment.is_image,
            "image_width": attachment.image_width,
            "image_height": attachment.image_height,
            "usage_type": attachment.usage_type,
            "description": attachment.description,
            "status": attachment.status,
            "file_url": attachment.file_url,
            "url_expires_at": attachment.url_expires_at,
            "created_by": attachment.created_by,
            "created_at": attachment.created_at,
            "updated_by": attachment.updated_by,
            "updated_at": attachment.updated_at,
        }
        
        return Attachment(**attachment_dict)

    async def get_ticket_attachments(
        self,
        ticket_id: int,
        usage_type: Optional[str] = None
    ) -> List[Attachment]:
        """獲取 ticket 的附件列表"""
        attachments = await self.attachment_repository.get_by_ticket_id(
            ticket_id=ticket_id,
            usage_type=usage_type
        )
        
        result = []
        for attachment in attachments:
            # 檢查並更新過期的 URL
            if attachment.url_expires_at and attachment.url_expires_at < datetime.now():
                file_url = self.minio_service.get_file_url(
                    bucket=attachment.bucket_name,
                    file_path=attachment.file_path
                )
                attachment.file_url = file_url
                attachment.url_expires_at = datetime.now() + timedelta(seconds=settings.file_url_expiry)
            
            attachment_dict = {
                "id": attachment.id,
                "ticket_id": attachment.ticket_id,
                "file_name": attachment.file_name,
                "file_path": attachment.file_path,
                "bucket_name": attachment.bucket_name,
                "file_size": attachment.file_size,
                "mime_type": attachment.mime_type,
                "is_image": attachment.is_image,
                "image_width": attachment.image_width,
                "image_height": attachment.image_height,
                "usage_type": attachment.usage_type,
                "description": attachment.description,
                "status": attachment.status,
                "file_url": attachment.file_url,
                "url_expires_at": attachment.url_expires_at,
                "created_by": attachment.created_by,
                "created_at": attachment.created_at,
                "updated_by": attachment.updated_by,
                "updated_at": attachment.updated_at,
            }
            result.append(Attachment(**attachment_dict))
        
        return result

    async def delete_attachment(self, attachment_id: int, user_id: int) -> Tuple[bool, str]:
        """刪除附件"""
        try:
            attachment = await self.attachment_repository.get_by_id(attachment_id)
            if not attachment:
                return False, "附件不存在"
            
            # 檢查權限
            # if attachment.created_by != user_id:
            #     return False, "無權限刪除此附件"
            
            # 從 MinIO 刪除檔案
            success, message = await self.minio_service.delete_file(
                bucket=attachment.bucket_name,
                file_path=attachment.file_path
            )
            
            if not success:
                return False, f"刪除檔案失敗: {message}"
            
            # 軟刪除資料庫記錄
            await self.attachment_repository.soft_delete(attachment_id, user_id)
            
            return True, "附件刪除成功"
            
        except Exception as e:
            return False, f"刪除附件失敗: {str(e)}"

    async def update_attachment(
        self,
        attachment_id: int,
        attachment_update: AttachmentUpdate,
        user_id: int
    ) -> Optional[Attachment]:
        """更新附件資訊"""
        attachment = await self.attachment_repository.update(
            id=attachment_id,
            update_data=attachment_update,
            user_id=user_id
        )
        
        if not attachment:
            return None
        
        attachment_dict = {
            "id": attachment.id,
            "ticket_id": attachment.ticket_id,
            "file_name": attachment.file_name,
            "file_path": attachment.file_path,
            "bucket_name": attachment.bucket_name,
            "file_size": attachment.file_size,
            "mime_type": attachment.mime_type,
            "is_image": attachment.is_image,
            "image_width": attachment.image_width,
            "image_height": attachment.image_height,
            "usage_type": attachment.usage_type,
            "description": attachment.description,
            "status": attachment.status,
            "file_url": attachment.file_url,
            "url_expires_at": attachment.url_expires_at,
            "created_by": attachment.created_by,
            "created_at": attachment.created_at,
            "updated_by": attachment.updated_by,
            "updated_at": attachment.updated_at,
        }
        
        return Attachment(**attachment_dict)

    async def download_file(self, attachment_id: int, user_id: int) -> Tuple[bool, bytes, str, str]:
        """
        下載檔案
        
        Returns:
            (success, file_content, filename, content_type)
        """
        try:
            attachment = await self.attachment_repository.get_by_id(attachment_id)
            if not attachment:
                return False, b"", "", ""
            
            # 檢查權限
            # if attachment.created_by != user_id:
            #     return False, b"", "", ""
            
            # 從 MinIO 下載檔案
            success, file_content, metadata = await self.minio_service.download_file(
                bucket=attachment.bucket_name,
                file_path=attachment.file_path
            )
            
            if not success:
                return False, b"", "", ""
            
            return True, file_content, attachment.file_name, attachment.mime_type
            
        except Exception as e:
            return False, b"", "", ""

    async def cleanup_orphaned_attachments(self, hours: int = 24) -> int:
        """清理孤立的附件 (背景任務用)"""
        try:
            orphaned_attachments = await self.attachment_repository.get_orphaned_attachments(hours)
            
            deleted_count = 0
            for attachment in orphaned_attachments:
                # 從 MinIO 刪除檔案
                await self.minio_service.delete_file(
                    bucket=attachment.bucket_name,
                    file_path=attachment.file_path
                )
                
                # 硬刪除資料庫記錄
                await self.attachment_repository.hard_delete(attachment.id)
                deleted_count += 1
            
            return deleted_count
            
        except Exception as e:
            print(f"清理孤立附件失敗: {e}")
            return 0