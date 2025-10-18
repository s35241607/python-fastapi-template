from __future__ import annotations

from collections.abc import Sequence
from typing import Any, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, InstrumentedAttribute

# --- 泛型定義 ---
ModelType = TypeVar("ModelType", bound=DeclarativeBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
ReadSchemaType = TypeVar("ReadSchemaType", bound=BaseModel)


class BaseRepository[
    ModelType: DeclarativeBase,
    CreateSchemaType: BaseModel,
    UpdateSchemaType: BaseModel,
    ReadSchemaType: BaseModel,
]:
    """
    通用 Repository，提供 CRUD 與 soft delete 功能。
    """

    model: type[ModelType]

    def __init__(
        self,
        db: AsyncSession,
        schema: type[ReadSchemaType] | None = None,
        auto_convert: bool = True,
    ) -> None:
        self.db: AsyncSession = db
        self.schema: type[ReadSchemaType] | None = schema
        self._auto_convert: bool = auto_convert

    # -------------------------
    # Internal helpers
    # -------------------------
    def _convert_one(self, obj: ModelType | None) -> ModelType | ReadSchemaType | None:
        if obj is None or not self._auto_convert:
            return obj
        if not self.schema:
            raise RuntimeError("Schema class must be provided for conversion.")
        return self.schema.model_validate(obj, from_attributes=True)

    def _convert_many(
        self,
        objs: Sequence[ModelType],
    ) -> list[ModelType] | list[ReadSchemaType]:
        if not self._auto_convert:
            return list(objs)
        if not self.schema:
            raise RuntimeError("Schema class must be provided for conversion.")
        return [self.schema.model_validate(item, from_attributes=True) for item in objs]

    def _extract_data_from_input(
        self,
        obj_in: CreateSchemaType | UpdateSchemaType | ModelType | dict[str, Any],
    ) -> dict[str, Any]:
        if isinstance(obj_in, dict):
            return {str(k): v for k, v in obj_in.items()}
        elif hasattr(obj_in, "model_dump") and callable(getattr(obj_in, "model_dump", None)):
            return obj_in.model_dump()  # type: ignore[attr-defined]
        elif hasattr(obj_in, "__dict__"):
            return {k: v for k, v in obj_in.__dict__.items() if not k.startswith("_") and k != "registry"}
        else:
            raise TypeError(f"Unsupported input type: {type(obj_in)}")

    # -------------------------
    # CRUD methods
    # -------------------------
    async def get_by_id(
        self,
        obj_id: Any,
        include_deleted: bool = False,
        options: list[Any] | None = None,
    ) -> ModelType | ReadSchemaType | None:
        stmt = select(self.model).where(self.model.id == obj_id)  # type: ignore[attr-defined]

        if options:
            stmt = stmt.options(*options)

        if not include_deleted and hasattr(self.model, "is_deleted"):
            stmt = stmt.where(not self.model.is_deleted)  # type: ignore[attr-defined]
        result = await self.db.execute(stmt)
        return self._convert_one(result.scalar_one_or_none())

    async def get_by_ids(
        self,
        ids: Sequence[int],
        include_deleted: bool = False,
        options: list[Any] | None = None,
    ) -> list[ModelType]:
        if not ids:
            return []
        stmt = select(self.model).where(self.model.id.in_(ids))  # type: ignore[attr-defined]

        if options:
            stmt = stmt.options(*options)

        if not include_deleted and hasattr(self.model, "is_deleted"):
            stmt = stmt.where(not self.model.is_deleted)  # type: ignore[attr-defined]
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_all(
        self,
        include_deleted: bool = False,
        options: list[Any] | None = None,
    ) -> list[ModelType] | list[ReadSchemaType]:
        stmt = select(self.model)

        if options:
            stmt = stmt.options(*options)

        if not include_deleted and hasattr(self.model, "is_deleted"):
            stmt = stmt.where(not self.model.is_deleted)  # type: ignore[attr-defined]
        result = await self.db.execute(stmt)
        return self._convert_many(result.scalars().all())

    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
        include_deleted: bool = False,
        options: list[Any] | None = None,
    ) -> list[ModelType] | list[ReadSchemaType]:
        stmt = select(self.model)

        if options:
            stmt = stmt.options(*options)

        if not include_deleted and hasattr(self.model, "is_deleted"):
            stmt = stmt.where(not self.model.is_deleted)  # type: ignore[attr-defined]

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    stmt = stmt.where(getattr(self.model, field) == value)
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return self._convert_many(result.scalars().all())

    async def create(
        self,
        obj_in: CreateSchemaType | ModelType | dict[str, Any],
        user_id: int | None = None,
        preload: list[InstrumentedAttribute[Any]] | None = None,
    ) -> ModelType | ReadSchemaType:
        if isinstance(obj_in, self.model):
            db_obj: ModelType = obj_in
        else:
            data = self._extract_data_from_input(obj_in)
            db_obj = self.model(**data)  # type: ignore[call-arg]

        if hasattr(db_obj, "created_by") and user_id:
            db_obj.created_by = user_id  # type: ignore

        self.db.add(db_obj)
        await self.db.flush()

        if preload:
            attribute_names: list[str] = [attr.key for attr in preload]  # 型別安全轉成字串
            await self.db.refresh(db_obj, attribute_names=attribute_names)
        else:
            await self.db.refresh(db_obj)
        return self._convert_one(db_obj)  # type: ignore[return-value]

    async def update(
        self,
        obj_id: Any,
        obj_in: UpdateSchemaType | ModelType | dict[str, Any],
        user_id: int | None = None,
    ) -> ModelType | ReadSchemaType | None:
        db_obj = await self._get_model_by_id(obj_id, include_deleted=True)
        if not db_obj:
            return None

        data = (
            obj_in.model_dump(exclude_unset=True)  # type: ignore[union-attr]
            if isinstance(obj_in, BaseModel)
            else self._extract_data_from_input(obj_in)
        )
        for field, value in data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        if hasattr(db_obj, "updated_by") and user_id:
            db_obj.updated_by = user_id  # type: ignore

        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return self._convert_one(db_obj)

    async def delete(self, obj_id: Any) -> ModelType | ReadSchemaType | None:
        """
        真正刪除資料，不做 soft delete
        """
        obj = await self._get_model_by_id(obj_id, include_deleted=True)
        if obj:
            await self.db.delete(obj)
            await self.db.flush()
        return self._convert_one(obj)

    async def soft_delete(self, obj_id: Any, user_id: int | None = None) -> ModelType | ReadSchemaType | None:
        """
        軟刪除，設定 is_deleted 為 True
        """
        obj = await self._get_model_by_id(obj_id)
        if obj:
            obj.is_deleted = True  # type: ignore
            self.db.add(obj)
            await self.db.flush()
            await self.db.refresh(obj)
            return self._convert_one(obj)
        return None

    # -------------------------
    # Private helpers
    # -------------------------
    async def _get_model_by_id(
        self,
        obj_id: Any,
        include_deleted: bool = False,
    ) -> ModelType | None:
        stmt = select(self.model).where(self.model.id == obj_id)  # type: ignore[attr-defined]
        if not include_deleted and hasattr(self.model, "is_deleted"):
            stmt = stmt.where(not self.model.is_deleted)  # type: ignore[attr-defined]
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
