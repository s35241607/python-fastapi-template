"""
app.repositories.base_repository
---------------------------------
通用 BaseRepository：提供通用的 CRUD、分頁(pagination)與軟刪除(soft delete)功能。

此檔案包含一個以泛型實作的 Repository 基底類別，旨在讓不同的 Model 可共享 CRUD 與分頁邏輯。
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, TypeVar, cast

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, InstrumentedAttribute

from app.schemas.pagination import PaginationQuery
from app.schemas.response import PaginationResponse

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
    通用 Repository 基底類別

    使用泛型 (generic types) 以便不同的 ORM Model 與 Pydantic Schema 能共用相同的 CRUD 與分頁邏輯。

    注意事項：
    - 若啟用 auto_convert，請於建構時提供對應的 Pydantic schema。
    - 本類別不會在內部呼叫 commit，commit/rollback 應由 service 或外層交易管理。
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
    # 內部輔助方法
    # -------------------------
    def _convert_one(self, obj: ModelType | None) -> ModelType | ReadSchemaType | None:
        """
        將單一 ORM 物件轉換成 Pydantic schema（若啟用 auto_convert）。

        若 obj 為 None 或者 auto_convert 被關閉，直接回傳原始物件。

        Args:
            obj: ORM model 實例或 None

        Returns:
            若 auto_convert 則回傳對應的 Pydantic schema，否則回傳原始 ORM 物件或 None
        """
        if obj is None or not self._auto_convert:
            return obj
        if not self.schema:
            raise RuntimeError("Schema class must be provided for conversion.")
        return self.schema.model_validate(obj, from_attributes=True)

    def _convert_many(
        self,
        objs: Sequence[ModelType],
    ) -> list[ModelType] | list[ReadSchemaType]:
        """
        將多個 ORM 物件轉換成 Pydantic schema list（若啟用 auto_convert）。

        Args:
            objs: ORM model 實例的可迭代序列

        Returns:
            List[ReadSchemaType] 或 List[ModelType]（視 auto_convert 而定）
        """
        if not self._auto_convert:
            return list(objs)
        if not self.schema:
            raise RuntimeError("Schema class must be provided for conversion.")
        return [self.schema.model_validate(item, from_attributes=True) for item in objs]

    # -------------------------
    # 私有輔助方法
    # -------------------------
    def _apply_filters(self, statement: Any, fdict: dict[str, Any] | None) -> Any:
        """
        將簡單的等於過濾器應用到 SQLAlchemy 的 selectable 或 statement（查詢物件）。

        Args:
            statement: SQLAlchemy 的 selectable 或 statement（查詢物件）
            fdict: 欄位 -> 值 的過濾字典

        Returns:
            經過過濾器處理後的 SQLAlchemy 查詢語句
        """
        if not fdict:
            return statement
        for field, value in fdict.items():
            if hasattr(self.model, field):
                statement = statement.where(getattr(self.model, field) == value)
        return statement

    async def _count_for_filters(self, filters: dict[str, Any] | None, include_deleted: bool) -> int:
        """
        計算符合 filters 的總數。

        Args:
            filters: 欄位->值 的過濾字典
            include_deleted: 是否包含已被軟刪除的項目

        Returns:
            總筆數 (int)
        """
        from sqlalchemy import func

        count_stmt = select(func.count()).select_from(self.model)
        if not include_deleted and hasattr(self.model, "is_deleted"):
            count_stmt = count_stmt.where(self.model.is_deleted.is_(False))  # type: ignore[attr-defined]
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    count_stmt = count_stmt.where(getattr(self.model, field) == value)
        count_res = await self.db.execute(count_stmt)
        return int(count_res.scalar_one())

    async def _get_model_by_id(
        self,
        obj_id: Any,
        include_deleted: bool = False,
    ) -> ModelType | None:
        """
        內部使用：根據 id 取得 ORM model（可選擇包含已軟刪除）。

        參數:
            obj_id: 要查詢的主鍵 ID
            include_deleted: 是否包含軟刪除物件

        回傳:
            若找到則回傳 ORM model，否則回傳 None
        """
        stmt = select(self.model).where(self.model.id == obj_id)  # type: ignore[attr-defined]
        if not include_deleted and hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted.is_(False))  # type: ignore[attr-defined]
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    def _extract_data_from_input(
        self,
        obj_in: CreateSchemaType | UpdateSchemaType | ModelType | dict[str, Any],
    ) -> dict[str, Any]:
        """
        從不同輸入類型擷取可寫入 model 的欄位資料。

        支援型別：
        - dict: 直接使用
        - Pydantic model (有 model_dump): 使用 model_dump()
        - ORM model: 從 __dict__ 擷取公開屬性（排除以 _ 開頭及 registry）

        Args:
            obj_in: Create/Update schema、ORM instance 或 dict

        Returns:
            dict: 可用於 model 建構或更新的欄位字典

        Raises:
            TypeError: 當輸入類型不受支援時拋出
        """
        if isinstance(obj_in, dict):
            return {str(k): v for k, v in obj_in.items()}
        elif hasattr(obj_in, "model_dump") and callable(getattr(obj_in, "model_dump", None)):
            return obj_in.model_dump()  # type: ignore[attr-defined]
        elif hasattr(obj_in, "__dict__"):
            return {k: v for k, v in obj_in.__dict__.items() if not k.startswith("_") and k != "registry"}
        else:
            raise TypeError(f"Unsupported input type: {type(obj_in)}")

    # -------------------------
    # CRUD 方法
    # -------------------------
    async def get_by_id(
        self,
        obj_id: Any,
        include_deleted: bool = False,
        options: list[Any] | None = None,
    ) -> ModelType | ReadSchemaType | None:
        """
        根據 ID 查詢單一物件。

        Args:
            obj_id: 要查詢的主鍵 ID
            include_deleted: 是否包含軟刪除的物件（若 model 支援 is_deleted）
            options: SQLAlchemy 查詢選項（例如 joinedload）

        Returns:
            指定的 Model 或對應的 Pydantic schema，若不存在則回傳 None
        """
        stmt = select(self.model).where(self.model.id == obj_id)  # type: ignore[attr-defined]

        if options:
            stmt = stmt.options(*options)

        if not include_deleted and hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted.is_(False))  # type: ignore[attr-defined]
        result = await self.db.execute(stmt)
        return self._convert_one(result.scalar_one_or_none())

    async def get_by_ids(
        self,
        ids: Sequence[int],
        include_deleted: bool = False,
        options: list[Any] | None = None,
    ) -> list[ModelType]:
        """
        批次查詢多個 ID 的物件。

        Args:
            ids: 要查詢的 ID 序列
            include_deleted: 是否包含軟刪除的物件
            options: SQLAlchemy 查詢 options

        Returns:
            Model 實例清單（未自動轉換為 schema；若需轉換，可於呼叫端設定）
        """
        if not ids:
            return []
        stmt = select(self.model).where(self.model.id.in_(ids))  # type: ignore[attr-defined]

        if options:
            stmt = stmt.options(*options)

        if not include_deleted and hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted.is_(False))  # type: ignore[attr-defined]
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_all(
        self,
        include_deleted: bool = False,
        options: list[Any] | None = None,
    ) -> list[ModelType] | list[ReadSchemaType]:
        """
        取得所有（或未被軟刪除）的資料。

        Args:
            include_deleted: 是否包含已軟刪除的資料
            options: SQLAlchemy query options

        Returns:
            List[ModelType] 或 List[ReadSchemaType]（視 auto_convert 而定）
        """
        stmt = select(self.model)

        if options:
            stmt = stmt.options(*options)

        if not include_deleted and hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted.is_(False))  # type: ignore[attr-defined]
        result = await self.db.execute(stmt)
        return self._convert_many(result.scalars().all())

    async def get_paginated(  # noqa: C901  # 函式複雜度可接受
        self,
        query: PaginationQuery,
        include_deleted: bool = False,
        options: list[Any] | None = None,
    ) -> PaginationResponse[ReadSchemaType]:
        """
        以 PaginationQuery 取得分頁結果的通用查詢方法。

        行為：
        - 透過 query.extract_filters() 取得過濾器
        - 支援排序（sort_by, sort_order）與分頁（page, page_size）
        - 若 model 支援 is_deleted，預設會排除已軟刪除的資料

        參數:
            query: 包含分頁、排序與過濾資訊的 PaginationQuery
            include_deleted: 是否包含軟刪除資料
            options: SQLAlchemy query options

        回傳:
            PaginationResponse[ReadSchemaType]：包含分頁 metadata 與轉換後的 items
        """
        stmt = select(self.model)

        if options:
            stmt = stmt.options(*options)

        if not include_deleted and hasattr(self.model, "is_deleted"):
            stmt = stmt.where(self.model.is_deleted.is_(False))  # type: ignore[attr-defined]

        # 從 PaginationQuery 物件擷取過濾、排序與分頁參數
        filters = query.extract_filters()
        page, page_size = query.pagination()
        sort_by, sort_order = query.sort()

        # 應用過濾條件
        # 移除值為 None 的過濾條件以避免空值比對
        if filters:
            filters = {k: v for k, v in filters.items() if v is not None}

        # 使用類別層級的私有輔助方法來應用過濾
        stmt = self._apply_filters(stmt, filters)

        # 若排序欄位存在則應用排序
        if sort_by and hasattr(self.model, sort_by):
            col = getattr(self.model, sort_by)
            stmt = stmt.order_by(col.asc() if sort_order and sort_order.lower() == "asc" else col.desc())

        # 計算符合條件的總數，用於分頁 metadata
        # 計算總數（使用類別層級私有輔助方法）
        total = await self._count_for_filters(filters, include_deleted)

        # 應用分頁：計算頁面偏移與分頁大小
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        result = await self.db.execute(stmt)
        items = result.scalars().all()
        converted = self._convert_many(items)

        # 建立分頁資訊（總頁數、是否有上一頁/下一頁等）
        total_pages = (total + page_size - 1) // page_size if page_size else 1
        has_next = page < total_pages
        has_prev = page > 1

        return PaginationResponse[ReadSchemaType](
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev,
            items=list(cast(list[ReadSchemaType], converted)),
        )

    async def create(
        self,
        obj_in: CreateSchemaType | ModelType | dict[str, Any],
        user_id: int | None = None,
        preload: list[InstrumentedAttribute[Any]] | None = None,
    ) -> ModelType | ReadSchemaType:
        """
        建立資料並回傳已建立的物件（或 schema）。

        Args:
            obj_in: Create schema、ORM instance 或 dict
            user_id: 當 model 有 created_by 欄位時，會填入該 user_id
            preload: 若需預先載入關聯欄位，可在此提供 InstrumentedAttribute 清單

        Returns:
            建立後的 Model 或 ReadSchemaType（取決於 auto_convert 設定）
        """
        if isinstance(obj_in, self.model):
            db_obj: ModelType = obj_in
        else:
            data = self._extract_data_from_input(obj_in)
            db_obj = self.model(**data)  # type: ignore[call-arg]

        if hasattr(db_obj, "created_by") and user_id:
            db_obj.created_by = user_id  # type: ignore

        # 自動設置 created_at（若欄位存在）
        if hasattr(db_obj, "created_at"):
            from datetime import datetime

            db_obj.created_at = datetime.utcnow()  # type: ignore

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
        preload: list[InstrumentedAttribute[Any]] | None = None,
    ) -> ModelType | ReadSchemaType | None:
        """
        更新指定 ID 的物件。

        Args:
            obj_id: 要更新的主鍵 ID
            obj_in: Update schema、ORM instance 或 dict（支援 Pydantic 的 exclude_unset）
            user_id: 若 model 有 updated_by 欄位，會填入該 user_id

        Returns:
            更新後的 Model 或 ReadSchemaType，若找不到則回傳 None
        """
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

        # 自動設置 updated_at（若欄位存在）
        if hasattr(db_obj, "updated_at"):
            from datetime import datetime

            db_obj.updated_at = datetime.utcnow()  # type: ignore

        self.db.add(db_obj)
        await self.db.flush()

        if preload:
            attribute_names: list[str] = [attr.key for attr in preload]  # 型別安全轉成字串
            await self.db.refresh(db_obj, attribute_names=attribute_names)
        else:
            await self.db.refresh(db_obj)
        return self._convert_one(db_obj)

    async def delete(self, obj_id: Any) -> ModelType | ReadSchemaType | None:
        """
        硬刪除（真正從資料庫移除）。

        注意：若需要保留紀錄，請使用 soft_delete()。
        """
        obj = await self._get_model_by_id(obj_id, include_deleted=True)
        if obj:
            await self.db.delete(obj)
            await self.db.flush()
        return self._convert_one(obj)

    async def soft_delete(self, obj_id: Any, user_id: int | None = None) -> ModelType | ReadSchemaType | None:
        """
        軟刪除：將物件的 is_deleted 設為 True。

        若你的 model 同時有 deleted_by/deleted_at 等欄位，建議於 service 層補足相應欄位的更新。
        """
        obj = await self._get_model_by_id(obj_id)
        if obj:
            obj.is_deleted = True  # type: ignore
            self.db.add(obj)
            await self.db.flush()
            await self.db.refresh(obj)
            return self._convert_one(obj)
        return None
