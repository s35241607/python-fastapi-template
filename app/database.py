from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from app.config import settings

# 創建 async engine - 如果沒有設定，使用 SQLite 進行測試
database_url = settings.database_url or "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(
    database_url,
    echo=settings.debug,
    future=True,
)

# 創建 async session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# 依賴注入函數，用於 FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
