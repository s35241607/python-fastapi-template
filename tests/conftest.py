import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

def pytest_configure(config):
    """
    This hook runs before pytest collects tests, allowing for early setup.
    We patch the settings here to ensure that all modules get the test
    configuration when they are first imported.
    """
    # Import the module, not the object, so we can patch it
    import app.config
    from app.config import Settings

    # Override the settings object in the config module
    app.config.settings = Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        db_schema=None,  # SQLite does not support schemas
    )

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_test_db() -> AsyncGenerator[None, None]:
    """
    Fixture to create and tear down the test database schema for each test.
    It imports the engine locally to ensure it uses the patched settings.
    """
    from app.database import engine
    from app.models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
    """
    Provides a TestClient for making API requests. This fixture handles
    all necessary setup, including dependency overrides for the database
    and authentication.
    """
    from app.main import app
    from app.database import get_db, engine
    from app.auth.dependencies import get_user_id_from_jwt

    TestSessionLocal = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with TestSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    def override_get_user_id():
        return 1  # Simulate user with ID 1

    # Apply overrides for the duration of the test
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_user_id_from_jwt] = override_get_user_id

    with TestClient(app) as c:
        yield c

    # Clean up overrides after the test
    app.dependency_overrides.clear()