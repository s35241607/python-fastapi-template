from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# 泛型定義 - 移除 bound 約束，保持簡單
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
ReadSchemaType = TypeVar("ReadSchemaType", bound=BaseModel)


class BaseRepository[ModelType, CreateSchemaType: BaseModel, UpdateSchemaType: BaseModel, ReadSchemaType: BaseModel]:
    """
    通用 Repository，Session 在初始化時注入。
    """

    # model 屬性將由子類別提供
    model: Any

    def __init__(self, db: AsyncSession, schema: type[ReadSchemaType] | None = None, *, auto_convert: bool = True):
        """
        初始化時注入 AsyncSession。
        """
        self.db = db
        self.schema = schema
        self._auto_convert = auto_convert

    def _convert_one(self, obj: ModelType | None) -> ModelType | ReadSchemaType | None:
        if obj is None or not self._auto_convert:
            return obj
        if not self.schema:
            raise RuntimeError("Schema class must be provided for automatic conversion.")
        return self.schema.model_validate(obj, from_attributes=True)

    def _convert_many(self, objs: Sequence[ModelType]) -> list[ModelType] | list[ReadSchemaType]:
        if not self._auto_convert:
            return list(objs)
        if not self.schema:
            raise RuntimeError("Schema class must be provided for automatic conversion.")
        return [self.schema.model_validate(item, from_attributes=True) for item in objs]

    async def get_by_id(self, obj_id: Any, include_deleted: bool = False) -> ModelType | ReadSchemaType | None:
        """
        方法不再需要傳入 db。
        """
        statement = select(self.model).where(self.model.id == obj_id)
        if not include_deleted:
            statement = statement.where(self.model.deleted_at.is_(None))
        result = await self.db.execute(statement)  # 使用 self.db
        return self._convert_one(result.scalar_one_or_none())

    async def get_all(self, include_deleted: bool = False) -> list[ModelType] | list[ReadSchemaType]:
        statement = select(self.model)
        if not include_deleted:
            statement = statement.where(self.model.deleted_at.is_(None))
        result = await self.db.execute(statement)  # 使用 self.db
        return self._convert_many(result.scalars().all())

    async def get_multi(
        self, skip: int = 0, limit: int = 100, filters: dict[str, Any] | None = None, include_deleted: bool = False
    ) -> list[ModelType] | list[ReadSchemaType]:
        statement = select(self.model)
        if not include_deleted:
            statement = statement.where(self.model.deleted_at.is_(None))
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    statement = statement.where(getattr(self.model, field) == value)

        statement = statement.offset(skip).limit(limit)
        result = await self.db.execute(statement)  # 使用 self.db
        return self._convert_many(result.scalars().all())

    async def create(self, obj_in: CreateSchemaType, user_id: int | None = None) -> ModelType | ReadSchemaType:
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        db_obj_any: Any = db_obj
        if user_id:
            db_obj_any.created_by = user_id
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return self._convert_required(db_obj)

    async def update(
        self, obj_id: Any, obj_in: UpdateSchemaType | dict[str, Any], user_id: int | None = None
    ) -> ModelType | ReadSchemaType | None:
        """
        Updates an object by its ID.
        """
        db_obj = await self._get_model_by_id(obj_id=obj_id)
        if not db_obj:
            return None
        db_obj_any: Any = db_obj

        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(db_obj_any, field):
                setattr(db_obj_any, field, value)
        if user_id:
            db_obj_any.updated_by = user_id

        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return self._convert_required(db_obj)

    async def delete(self, obj_id: Any) -> ModelType | ReadSchemaType | None:
        obj = await self._get_model_by_id(obj_id=obj_id, include_deleted=True)
        if obj:
            await self.db.delete(obj)
            await self.db.flush()
        return self._convert_one(obj)

    async def soft_delete(self, obj_id: Any, user_id: int | None = None) -> ModelType | ReadSchemaType | None:
        obj = await self._get_model_by_id(obj_id=obj_id)
        if obj:
            obj_any: Any = obj
            obj_any.deleted_at = datetime.now(UTC)
            if user_id:
                obj_any.deleted_by = user_id
            self.db.add(obj)
            await self.db.flush()
            await self.db.refresh(obj)
            return self._convert_required(obj)
        return None

    async def _get_model_by_id(self, obj_id: Any, include_deleted: bool = False) -> ModelType | None:
        statement = select(self.model).where(self.model.id == obj_id)
        if not include_deleted:
            statement = statement.where(self.model.deleted_at.is_(None))
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    def _convert_required(self, obj: ModelType) -> ModelType | ReadSchemaType:
        converted = self._convert_one(obj)
        if converted is None:
            raise RuntimeError("Conversion returned None for required object.")
        return converted
