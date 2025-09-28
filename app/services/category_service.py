from typing import cast

from fastapi import Depends, HTTPException

from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate


class CategoryService:
    def __init__(self, category_repo: CategoryRepository = Depends(CategoryRepository)):
        """Service is constructed with a CategoryRepository instance.

        Contract:
        - inputs: CategoryRepositoryS
        - outputs: domain models (Category) or primitives
        - error modes: passes through repository exceptions as appropriate
        """

        self.category_repo = category_repo

    async def create_category(self, category_create: CategoryCreate, user_id: int | None = None) -> CategoryRead:
        exists = await self.category_repo.get_by_name(category_create.name)
        if exists:
            raise HTTPException(status_code=409, detail="Category with this name already exists.")
        return await self.category_repo.create(category_create, user_id)

    async def get_category(self, category_id: int) -> CategoryRead | None:
        return await self.category_repo.get_by_id(category_id)

    async def get_categories(self) -> list[CategoryRead]:
        return cast(list[CategoryRead], await self.category_repo.get_all())

    async def update_category(
        self, category_id: int, category_update: CategoryUpdate, user_id: int | None = None
    ) -> CategoryRead | None:
        return cast(
            CategoryRead | None,
            await self.category_repo.update(
                category_id,
                category_update,
                user_id=user_id,
            ),
        )

    async def soft_delete_category(self, category_id: int, user_id: int | None = None) -> bool:
        return await self.category_repo.soft_delete(category_id, user_id) is not None
