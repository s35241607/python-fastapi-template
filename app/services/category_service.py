
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.category_repo = CategoryRepository(session)

    async def create_category(self, category_data: CategoryCreate, user_id: int | None = None) -> Category:
        return await self.category_repo.create(obj_in=category_data, user_id=user_id)

    async def get_category(self, category_id: int) -> Category | None:
        return await self.category_repo.get_by_id(category_id)

    async def get_all_categories(self) -> list[Category]:
        return await self.category_repo.get_all()

    async def update_category(self, category_id: int, category_data: CategoryUpdate, user_id: int | None = None) -> Category | None:
        return await self.category_repo.update(obj_id=category_id, obj_in=category_data, user_id=user_id)

    async def soft_delete_category(self, category_id: int, user_id: int | None = None) -> Category | None:
        return await self.category_repo.soft_delete(obj_id=category_id, user_id=user_id)

    async def hard_delete_category(self, category_id: int) -> Category | None:
        return await self.category_repo.delete(obj_id=category_id)
