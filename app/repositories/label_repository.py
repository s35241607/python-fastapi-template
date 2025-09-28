from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.label import Label
from app.repositories.base_repository import BaseRepository
from app.schemas.label import LabelCreate, LabelRead, LabelUpdate


class LabelRepository(BaseRepository[Label, LabelCreate, LabelUpdate, LabelRead]):
    model = Label

    def __init__(self, session: AsyncSession = Depends(get_db)):
        """Repository depends on an AsyncSession provided by get_db."""
        super().__init__(session, schema=LabelRead)

    async def get_by_name(self, name: str, include_deleted: bool = False) -> Label | LabelRead | None:
        statement = select(self.model).where(self.model.name == name)
        if not include_deleted:
            statement = statement.where(self.model.deleted_at.is_(None))
        result = await self.db.execute(statement)
        return self._convert_one(result.scalar_one_or_none())
