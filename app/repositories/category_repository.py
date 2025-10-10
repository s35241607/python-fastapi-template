from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.category import Category
from app.repositories.base_repository import BaseRepository
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate


class CategoryRepository(BaseRepository[Category, CategoryCreate, CategoryUpdate, CategoryRead]):
    model = Category

    def __init__(self, session: AsyncSession = Depends(get_db)):
        """Repository depends on an AsyncSession provided by get_db."""
        super().__init__(session, schema=CategoryRead)

    async def get_by_name(self, name: str, include_deleted: bool = False) -> Category | CategoryRead | None:
        statement = select(self.model).where(self.model.name == name)
        if not include_deleted:
            statement = statement.where(self.model.is_deleted == False)
        result = await self.db.execute(statement)
        return self._convert_one(result.scalar_one_or_none())
