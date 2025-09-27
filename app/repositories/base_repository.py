from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# 泛型定義 - 移除 bound 約束，保持簡單
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    通用 Repository，Session 在初始化時注入。
    """

    # model 屬性將由子類別提供
    model: type[ModelType]

    def __init__(self, db: AsyncSession):
        """
        初始化時注入 AsyncSession。
        """
        self.db = db

    async def get_by_id(self, *, obj_id: Any, include_deleted: bool = False) -> ModelType | None:
        """
        方法不再需要傳入 db。
        """
        statement = select(self.model).where(self.model.id == obj_id)
        if not include_deleted:
            statement = statement.where(self.model.deleted_at.is_(None))

        result = await self.db.execute(statement)  # 使用 self.db
        return result.scalar_one_or_none()

    async def get_all(self, *, include_deleted: bool = False) -> list[ModelType]:
        statement = select(self.model)
        if not include_deleted:
            statement = statement.where(self.model.deleted_at.is_(None))
        result = await self.db.execute(statement)  # 使用 self.db
        return result.scalars().all()

    async def get_multi(
        self, *, skip: int = 0, limit: int = 100, filters: dict[str, Any] | None = None, include_deleted: bool = False
    ) -> list[ModelType]:
        statement = select(self.model)
        if not include_deleted:
            statement = statement.where(self.model.deleted_at.is_(None))
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    statement = statement.where(getattr(self.model, field) == value)

        statement = statement.offset(skip).limit(limit)
        result = await self.db.execute(statement)  # 使用 self.db
        return result.scalars().all()

    async def create(self, *, obj_in: CreateSchemaType, user_id: int | None = None) -> ModelType:
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        if user_id:
            db_obj.created_by = user_id
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, *, obj_id: Any, obj_in: UpdateSchemaType | dict, user_id: int | None = None) -> ModelType | None:
        """
        Updates an object by its ID.
        """
        db_obj = await self.get_by_id(obj_id=obj_id)
        if not db_obj:
            return None

        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        if user_id:
            db_obj.updated_by = user_id

        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, *, obj_id: Any) -> ModelType | None:
        obj = await self.get_by_id(obj_id=obj_id)
        if obj:
            await self.db.delete(obj)
            await self.db.flush()
        return obj

    async def soft_delete(self, *, obj_id: Any, user_id: int | None = None) -> ModelType | None:
        obj = await self.get_by_id(obj_id=obj_id)
        if obj:
            obj.deleted_at = datetime.now(datetime.UTC)
            if user_id:
                obj.deleted_by = user_id
            self.db.add(obj)
            await self.db.flush()
            await self.db.refresh(obj)
        return obj
