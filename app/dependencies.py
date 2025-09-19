from fastapi import Depends
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repository import UserRepository

def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)