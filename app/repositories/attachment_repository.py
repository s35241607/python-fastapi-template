from typing import cast

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.attachment import Attachment
from app.repositories.base_repository import BaseRepository
from app.schemas.attachment import AttachmentRead, AttachmentUpdate


class AttachmentRepository(BaseRepository[Attachment, Attachment, AttachmentUpdate, AttachmentRead]):
    model = Attachment

    def __init__(self, session: AsyncSession = Depends(get_db)):
        """Repository depends on an AsyncSession provided by get_db."""
        super().__init__(session, schema=AttachmentRead)

    async def get_by_related(self, related_type: str, related_id: int) -> list[AttachmentRead]:
        """根據關聯類型和 ID 取得附件"""
        stmt = select(self.model).where(
            self.model.related_type == related_type, self.model.related_id == related_id, self.model.is_deleted.is_(False)
        )
        result = await self.db.execute(stmt)
        return cast(list[AttachmentRead], self._convert_many(result.scalars().all()))

    async def get_by_ticket_id(self, ticket_id: int) -> list[AttachmentRead]:
        """根據 ticket ID 取得附件"""
        stmt = select(self.model).where(self.model.ticket_id == ticket_id, self.model.is_deleted.is_(False))
        result = await self.db.execute(stmt)
        return cast(list[AttachmentRead], self._convert_many(result.scalars().all()))
