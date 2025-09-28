from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

# 創建 async engine - 如果沒有設定，使用 SQLite 進行測試
database_url = settings.database_url or "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(
    database_url,
    echo=settings.debug,
    future=True,
    pool_pre_ping=True,  # 檢查連接健康
    pool_recycle=3600,  # 每小時回收連接
)

# 創建 async session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,  # 明確設置不自動 commit
    autoflush=False,  # 不自動 flush
)


# 依賴注入函數，用於 FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
