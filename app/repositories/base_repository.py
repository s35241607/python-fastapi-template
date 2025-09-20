from typing import Generic, TypeVar, Type, Optional, List, Any, Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.models.base import Base

# 泛型定義 - 移除 bound 約束，保持簡單
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    通用 Repository，Session 在初始化時注入。
    """
    # model 屬性將由子類別提供
    model: Type[ModelType]
    def __init__(self, db: AsyncSession):
        """
        初始化時注入 AsyncSession。
        """
        self.db = db

    async def get_by_id(self, *, id: Any, include_deleted: bool = False) -> Optional[ModelType]:
        """
        方法不再需要傳入 db。
        """
        statement = select(self.model).where(self.model.id == id)
        if not include_deleted:
            statement = statement.where(self.model.is_deleted == False)
        
        result = await self.db.execute(statement) # 使用 self.db
        return result.scalar_one_or_none()

    async def get_multi(
        self, 
        *, 
        skip: int = 0, 
        limit: int = 100, 
        filters: Optional[Dict[str, Any]] = None,
        include_deleted: bool = False
    ) -> List[ModelType]:
        statement = select(self.model)
        if not include_deleted:
            statement = statement.where(self.model.is_deleted == False)
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    statement = statement.where(getattr(self.model, field) == value)
        
        statement = statement.offset(skip).limit(limit)
        result = await self.db.execute(statement) # 使用 self.db
        return result.scalars().all()

    async def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, *, id: Any, obj_in: UpdateSchemaType | dict) -> Optional[ModelType]:
        """
        Updates an object by its ID.
        """
        db_obj = await self.get_by_id(id=id)
        if not db_obj:
            return None

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj
    
    async def delete(self, *, id: Any) -> Optional[ModelType]:
        obj = await self.get_by_id(id=id)
        if obj:
            await self.db.delete(obj)
            await self.db.flush()
        return obj

    async def soft_delete(self, *, id: Any) -> Optional[ModelType]:
        obj = await self.get_by_id(id=id)
        if obj:
            obj.soft_delete()
            self.db.add(obj)
            await self.db.flush()
            await self.db.refresh(obj)
        return obj