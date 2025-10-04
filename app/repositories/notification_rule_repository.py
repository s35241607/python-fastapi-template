from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.notification_rule import NotificationRule
from app.repositories.base_repository import BaseRepository
from app.schemas.notification import (
    NotificationRuleCreate,
    NotificationRuleRead,
    NotificationRuleUpdate,
)


class NotificationRuleRepository(
    BaseRepository[
        NotificationRule,
        NotificationRuleCreate,
        NotificationRuleUpdate,
        NotificationRuleRead,
    ]
):
    model = NotificationRule

    def __init__(self, db: AsyncSession = Depends(get_db)):
        super().__init__(db=db, schema=NotificationRuleRead)

    async def get_by_event(
        self, event: str, *, ticket_id: int | None = None, ticket_template_id: int | None = None
    ) -> list[NotificationRule]:
        """
        Get notification rules based on the event and either ticket_id or ticket_template_id.
        """
        statement = select(self.model).where(self.model.notify_on_event == event)

        if ticket_id:
            statement = statement.where(self.model.ticket_id == ticket_id)
        elif ticket_template_id:
            statement = statement.where(self.model.ticket_template_id == ticket_template_id)
        else:
            # Must provide at least one id to filter on
            return []

        result = await self.db.execute(statement)
        return list(result.scalars().all())