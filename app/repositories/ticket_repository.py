from datetime import UTC, datetime

from fastapi import Depends
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Ticket, TicketViewPermission
from app.models.enums import TicketVisibility
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

    async def get_by_ticket_no(self, ticket_no: str) -> Ticket | TicketRead | None:
        """根據工單號查詢工單"""
        statement = select(self.model).where(and_(self.model.ticket_no == ticket_no, self.model.deleted_at.is_(None)))
        result = await self.db.execute(statement)
        return self._convert_one(result.scalar_one_or_none())

    async def get_by_created_by(self, created_by: int) -> list[Ticket] | list[TicketRead]:
        """根據建立者查詢工單列表"""
        statement = select(self.model).where(and_(self.model.created_by == created_by, self.model.deleted_at.is_(None)))
        result = await self.db.execute(statement)
        return self._convert_many(result.scalars().all())

    async def get_tickets_for_user(self, user_id: int) -> list[Ticket] | list[TicketRead]:
        """
        取得使用者可見的工單列表
        - 內部工單 (internal)
        - 使用者有權限的受限工單 (restricted)
        """
        # 條件 1: 使用者是工單的建立者或被指派者
        user_is_participant = or_(self.model.created_by == user_id, self.model.assigned_to == user_id)

        # 條件 2: 使用者存在於 ticket_view_permissions 中
        user_has_explicit_permission = self.model.view_permissions.any(TicketViewPermission.user_id == user_id)

        # 組合受限工單的權限條件
        restricted_ticket_permission = and_(
            self.model.visibility == TicketVisibility.RESTRICTED,
            or_(user_is_participant, user_has_explicit_permission),
        )

        # 最終查詢條件: (工單是內部公開) 或 (使用者對受限工單有權限)
        final_filter = or_(
            self.model.visibility == TicketVisibility.INTERNAL,
            restricted_ticket_permission,
        )

        statement = (
            select(self.model)
            .where(and_(final_filter, self.model.deleted_at.is_(None)))
            .options(selectinload(self.model.categories), selectinload(self.model.labels))
            .order_by(self.model.created_at.desc())
        )

        result = await self.db.execute(statement)
        return self._convert_many(result.scalars().all())
