from typing import cast

from fastapi import Depends, HTTPException

from app.repositories.label_repository import LabelRepository
from app.schemas.label import LabelCreate, LabelRead, LabelUpdate


class LabelService:
    def __init__(self, label_repo: LabelRepository = Depends(LabelRepository)):
        """Service depends on a LabelRepository provided by Depends."""
        self.label_repo = label_repo

    async def create_label(self, label_create: LabelCreate, user_id: int | None = None) -> LabelRead:
        exists = await self.label_repo.get_by_name(label_create.name)
        if exists:
            raise HTTPException(status_code=409, detail="Label with this name already exists.")
        return await self.label_repo.create(label_create, user_id=user_id)

    async def get_label(self, label_id: int) -> LabelRead | None:
        return await self.label_repo.get_by_id(label_id)

    async def get_labels(self) -> list[LabelRead]:
        return cast(list[LabelRead], await self.label_repo.get_all())

    async def update_label(self, label_id: int, label_update: LabelUpdate, user_id: int | None = None) -> LabelRead | None:
        return cast(
            LabelRead | None,
            await self.label_repo.update(
                label_id,
                label_update,
                user_id=user_id,
            ),
        )

    async def soft_delete_label(self, label_id: int, user_id: int | None = None) -> bool:
        return await self.label_repo.soft_delete(label_id, user_id) is not None
