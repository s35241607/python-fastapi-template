from datetime import UTC, datetime
from typing import Any

from fastapi import Depends
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.ticket import Ticket
from app.repositories.base_repository import BaseRepository
from app.schemas.ticket import TicketCreate, TicketRead, TicketUpdate


class TicketRepository(BaseRepository[Ticket, TicketCreate, TicketUpdate, TicketRead]):
    model = Ticket

    def __init__(self, session: AsyncSession = Depends(get_db)):
        """Repository depends on an AsyncSession provided by get_db."""
        super().__init__(session, schema=TicketRead)

    async def generate_ticket_no(self) -> str:
        """生成唯一的工單號碼: TIC + YYYYMMDD + 流水號"""
        today: str = datetime.now(UTC).strftime("%Y%m%d")

        sql = (
            select(self.model.ticket_no)
            .where(self.model.ticket_no.like(f"TIC-{today}-%"))
            .order_by(self.model.ticket_no.desc())
            .limit(1)
        )

        result = await self.db.execute(sql)
        last_ticket_no: str | None = result.scalar_one_or_none()
        new_sequence_no = 1 if not last_ticket_no else int(last_ticket_no.split("-")[-1]) + 1

        return f"TIC-{today}-{new_sequence_no}"

    async def get_by_ticket_no(
        self,
        ticket_no: str,
        include_deleted: bool = False,
        options: list[Any] | None = None,
    ) -> Ticket | TicketRead | None:
        """
        根據工單號查詢工單，支援 include_deleted 與 SQLAlchemy options (例如 selectinload)

        Args:
            ticket_no: 工單號
            include_deleted: 是否包含已軟刪除
            options: SQLAlchemy 查詢 options
        """
        statement = select(self.model).where(self.model.ticket_no == ticket_no)
        if options:
            statement = statement.options(*options)
        if not include_deleted and hasattr(self.model, "is_deleted"):
            statement = statement.where(self.model.is_deleted.is_(False))
        result = await self.db.execute(statement)
        return self._convert_one(result.scalar_one_or_none())

    async def get_by_created_by(self, created_by: int) -> list[Ticket] | list[TicketRead]:
        """根據建立者查詢工單列表"""
        statement = select(self.model).where(and_(self.model.created_by == created_by, self.model.is_deleted.is_(False)))
        result = await self.db.execute(statement)
        return self._convert_many(result.scalars().all())
