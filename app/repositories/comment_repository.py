
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.comment import Comment
from app.repositories.base import BaseRepository


class CommentRepository(BaseRepository[Comment]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Comment)

    async def get_comments_by_ticket(self, ticket_id: int) -> list[Comment]:
        result = await self.session.execute(
            select(Comment).options(selectinload(Comment.user)).where(Comment.ticket_id == ticket_id)
        )
        return result.scalars().all()

    async def get_comments_by_user(self, user_id: int) -> list[Comment]:
        result = await self.session.execute(
            select(Comment).options(selectinload(Comment.ticket)).where(Comment.user_id == user_id)
        )
        return result.scalars().all()
