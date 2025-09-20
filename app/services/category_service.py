
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.category_repo = CategoryRepository(session)

    async def create_category(self, category_data: CategoryCreate) -> Category:
        category = Category(**category_data.model_dump())
        return await self.category_repo.create(category)

    async def get_category(self, category_id: int) -> Category | None:
        return await self.category_repo.get_by_id(category_id)

    async def get_all_categories(self) -> list[Category]:
        return await self.category_repo.get_all()

    async def update_category(self, category_id: int, category_data: CategoryUpdate) -> Category | None:
        return await self.category_repo.update(category_id, **category_data.model_dump(exclude_unset=True))

    async def delete_category(self, category_id: int) -> bool:
        return await self.category_repo.delete(category_id)
