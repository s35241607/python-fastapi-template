"""
附件 Repository
"""

from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.ticket_attachment import TicketAttachment
from app.repositories.base_repository import BaseRepository
from app.schemas.attachment import AttachmentCreate, AttachmentUpdate


class AttachmentRepository(BaseRepository[TicketAttachment, AttachmentCreate, AttachmentUpdate]):
    """附件 Repository"""

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.model = TicketAttachment

    async def get_by_ticket_id(
        self,
        ticket_id: int,
        include_deleted: bool = False,
        usage_type: Optional[str] = None
    ) -> List[TicketAttachment]:
        """根據 ticket ID 獲取附件列表"""
        conditions = [self.model.ticket_id == ticket_id]
        
        if not include_deleted:
            conditions.append(self.model.deleted_at.is_(None))
            
        if usage_type:
            conditions.append(self.model.usage_type == usage_type)
        
        query = select(self.model).where(and_(*conditions)).order_by(desc(self.model.created_at))
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_file_path(self, bucket_name: str, file_path: str) -> Optional[TicketAttachment]:
        """根據檔案路徑獲取附件"""
        query = select(self.model).where(
            and_(
                self.model.bucket_name == bucket_name,
                self.model.file_path == file_path,
                self.model.deleted_at.is_(None)
            )
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def create_attachment(
        self,
        ticket_id: Optional[int],
        file_name: str,
        file_path: str,
        bucket_name: str,
        file_size: int,
        mime_type: str,
        is_image: bool,
        usage_type: str,
        user_id: int,
        description: Optional[str] = None,
        image_width: Optional[int] = None,
        image_height: Optional[int] = None,
        file_url: Optional[str] = None,
        url_expires_at: Optional[datetime] = None
    ) -> TicketAttachment:
        """建立附件記錄"""
        attachment_data = {
            "ticket_id": ticket_id,
            "file_name": file_name,
            "file_path": file_path,
            "bucket_name": bucket_name,
            "file_size": file_size,
            "mime_type": mime_type,
            "is_image": is_image,
            "image_width": image_width,
            "image_height": image_height,
            "usage_type": usage_type,
            "description": description,
            "status": "completed",
            "file_url": file_url,
            "url_expires_at": url_expires_at,
            "created_by": user_id,
            "updated_by": user_id,
        }
        
        attachment = self.model(**attachment_data)
        self.db.add(attachment)
        await self.db.commit()
        await self.db.refresh(attachment)
        return attachment

    async def update_file_url(
        self,
        attachment_id: int,
        file_url: str,
        expires_at: datetime,
        user_id: int
    ) -> Optional[TicketAttachment]:
        """更新檔案 URL"""
        attachment = await self.get_by_id(attachment_id)
        if not attachment:
            return None
            
        attachment.file_url = file_url
        attachment.url_expires_at = expires_at
        attachment.updated_by = user_id
        attachment.updated_at = datetime.now()
        
        await self.db.commit()
        await self.db.refresh(attachment)
        return attachment

    async def get_expired_urls(self, buffer_minutes: int = 30) -> List[TicketAttachment]:
        """獲取 URL 即將過期的附件 (用於背景任務更新)"""
        threshold = datetime.now() + timedelta(minutes=buffer_minutes)
        
        query = select(self.model).where(
            and_(
                self.model.deleted_at.is_(None),
                self.model.url_expires_at < threshold,
                self.model.file_url.isnot(None)
            )
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_images_for_ticket(self, ticket_id: int) -> List[TicketAttachment]:
        """獲取指定 ticket 的圖片附件"""
        return await self.get_by_ticket_id(
            ticket_id=ticket_id,
            usage_type="inline_image"
        )

    async def get_attachments_for_ticket(self, ticket_id: int) -> List[TicketAttachment]:
        """獲取指定 ticket 的一般附件"""
        return await self.get_by_ticket_id(
            ticket_id=ticket_id,
            usage_type="attachment"
        )

    async def get_orphaned_attachments(self, hours: int = 24) -> List[TicketAttachment]:
        """獲取孤立的附件 (沒有關聯 ticket 且超過指定小時)"""
        threshold = datetime.now() - timedelta(hours=hours)
        
        query = select(self.model).where(
            and_(
                self.model.ticket_id.is_(None),
                self.model.created_at < threshold,
                self.model.deleted_at.is_(None)
            )
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()