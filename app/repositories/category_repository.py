from typing import Optional

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.category import Category
from app.repositories.base_repository import BaseRepository
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryRepository(BaseRepository[Category, CategoryCreate, CategoryUpdate]):
    def __init__(self, session: AsyncSession = Depends(get_db)):
        """Repository depends on an AsyncSession provided by get_db."""
        super().__init__(session)
        self.model = Category
