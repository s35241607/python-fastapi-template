"""
Global test configuration and shared fixtures using PostgreSQL

Tests use PostgreSQL (running on port 5433) which properly supports schema.
This ensures test environment matches production environment exactly.
"""

import os
from typing import Any

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

# ========== Database Configuration ==========

# PostgreSQL test database (supports schema, unlike SQLite)
# Running on port 5433 for testing, port 5432 for production
# Use environment variables for test database configuration
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5433/test_fastapi")

# Set test database URL at module level so it's available when app loads
os.environ["DATABASE_URL"] = TEST_DATABASE_URL


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create test database engine"""
    from app.models.base import Base

    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        pool_size=5,  # Allow more connections for session scope
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=30,
        pool_reset_on_return="rollback",
    )

    # Create schema and tables
    async with engine.begin() as conn:
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS ticket"))
        await conn.commit()

    async with engine.begin() as conn:

        def create_tables(connection: Any) -> None:
            Base.metadata.create_all(bind=connection)

        await conn.run_sync(create_tables)

    yield engine

    # Properly dispose of the engine
    await engine.dispose()


@pytest.fixture(scope="session")
def client():
    """Create sync HTTP client with test database"""
    from fastapi.testclient import TestClient

    from app.main import app as fastapi_app

    # Create sync client for testing
    with TestClient(app=fastapi_app, base_url="http://testserver") as test_client:
        yield test_client


@pytest_asyncio.fixture(scope="session")
async def async_db_session(test_engine):
    """Create async database session for testing"""
    async with AsyncSession(test_engine) as session:
        try:
            yield session
        finally:
            await session.rollback()


# ========== Event Loop Management ==========

# Note: pytest-asyncio handles event loop management automatically in strict mode
# No need for custom event_loop fixture


# ========== Test Users ==========


@pytest.fixture
def test_user_1() -> dict[str, str | int]:
    """Test user 1 (ticket creator)"""
    user_id = int(os.getenv("TEST_USER_ID_1", "1"))
    return {"id": user_id, "name": "User One", "email": "user1@example.com"}


@pytest.fixture
def test_user_2() -> dict[str, str | int]:
    """Test user 2 (non-creator)"""
    user_id = int(os.getenv("TEST_USER_ID_2", "2"))
    return {"id": user_id, "name": "User Two", "email": "user2@example.com"}


@pytest.fixture
def test_admin() -> dict[str, str | int]:
    """Test admin"""
    user_id = int(os.getenv("TEST_ADMIN_USER_ID", "99"))
    return {"id": user_id, "name": "Admin User", "email": "admin@example.com"}


# ========== JWT Token Fixtures ==========


@pytest.fixture
def create_token():
    """Create mock JWT token factory function"""
    from jose import jwt

    # Use environment variable for test JWT secret, fallback to fake_secret for testing
    test_jwt_secret = os.getenv("TEST_JWT_SECRET", "fake_secret")

    def _create_token(user_id: int = 1) -> str:
        # Create a valid JWT token with sub claim
        payload = {"sub": str(user_id), "type": "access"}
        token = jwt.encode(payload, test_jwt_secret, algorithm="HS256")
        return f"Bearer {token}"

    return _create_token


# ========== Auth Headers ==========


@pytest.fixture
def auth_headers(create_token):
    """Create auth headers for test user 1"""

    def _get_headers(user_id: int = 1) -> dict[str, str]:
        token = create_token(user_id)
        return {"Authorization": token}

    return _get_headers


# ========== Sample Data Fixtures ==========


@pytest.fixture
def sample_category(async_db_session):
    """建立樣本分類"""
    import uuid

    from app.models.category import Category

    # 使用異步會話創建樣本數據
    unique_name = f"Sample Bug Report {uuid.uuid4().hex[:8]}"
    category = Category(
        name=unique_name,
        description="Bug related issues",
        created_by=1,
    )
    async_db_session.add(category)
    async_db_session.commit()
    async_db_session.refresh(category)
    return category


@pytest.fixture
def sample_categories(test_engine):
    """建立多個樣本分類"""
    import uuid

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from app.models.category import Category

    # 使用同步引擎創建樣本數據
    sync_engine = create_engine(TEST_DATABASE_URL.replace("+asyncpg", ""))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

    with SessionLocal() as session:
        categories = [
            Category(
                name=f"Bug Report {uuid.uuid4().hex[:8]}",
                description="Bug related",
                created_by=1,
            ),
            Category(
                name=f"Feature Request {uuid.uuid4().hex[:8]}",
                description="Feature request",
                created_by=1,
            ),
            Category(
                name=f"Documentation {uuid.uuid4().hex[:8]}",
                description="Doc issues",
                created_by=1,
            ),
        ]
        session.add_all(categories)
        session.commit()
        for cat in categories:
            session.refresh(cat)
        return categories


@pytest.fixture
def sample_label(test_engine):
    """建立樣本標籤"""
    import uuid

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from app.models.label import Label

    # 使用同步引擎創建樣本數據
    sync_engine = create_engine(TEST_DATABASE_URL.replace("+asyncpg", ""))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

    with SessionLocal() as session:
        label_name = f"sample-critical-{uuid.uuid4().hex[:8]}"
        label = Label(name=label_name, color="#FF0000", description="Critical priority", created_by=1)
        session.add(label)
        session.commit()
        session.refresh(label)
        return label


@pytest.fixture
def sample_labels(test_engine):
    """建立多個樣本標籤"""
    import uuid

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from app.models.label import Label

    # 使用同步引擎創建樣本數據
    sync_engine = create_engine(TEST_DATABASE_URL.replace("+asyncpg", ""))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

    with SessionLocal() as session:
        labels = [
            Label(name=f"critical-{uuid.uuid4().hex[:8]}", color="#FF0000", description="Critical issue", created_by=1),
            Label(name=f"high-priority-{uuid.uuid4().hex[:8]}", color="#FFA500", description="High priority", created_by=1),
            Label(name=f"documentation-{uuid.uuid4().hex[:8]}", color="#0000FF", description="Doc related", created_by=1),
        ]
        session.add_all(labels)
        session.commit()
        for label in labels:
            session.refresh(label)
        return labels


@pytest.fixture
def sample_ticket(test_engine, sample_categories, sample_labels):
    """建立樣本工單"""
    import uuid

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from app.models.enums import TicketPriority, TicketStatus, TicketVisibility
    from app.models.ticket import Ticket

    # 使用同步引擎創建樣本數據
    sync_engine = create_engine(TEST_DATABASE_URL.replace("+asyncpg", ""))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

    with SessionLocal() as session:
        ticket = Ticket(
            ticket_no=f"TIC-20250101-{uuid.uuid4().hex[:3].upper()}",
            title="Sample Ticket",
            description="This is a sample ticket",
            status=TicketStatus.DRAFT,
            priority=TicketPriority.MEDIUM,
            visibility=TicketVisibility.INTERNAL,
            created_by=1,
            categories=[sample_categories[0]],  # 使用 sample_categories 的第一個
            labels=[sample_labels[0]],  # 使用 sample_labels 的第一個
        )
        session.add(ticket)
        session.commit()
        session.refresh(ticket)
        return ticket


@pytest.fixture(scope="function")
def sample_tickets(test_engine):
    """建立多個樣本工單"""
    import uuid

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from app.models.category import Category
    from app.models.enums import TicketPriority, TicketStatus, TicketVisibility
    from app.models.label import Label
    from app.models.ticket import Ticket

    # 使用同步引擎創建樣本數據，但確保不會與異步操作衝突
    sync_engine = create_engine(TEST_DATABASE_URL.replace("+asyncpg", ""))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

    with SessionLocal() as session:
        try:
            # 創建樣本分類和標籤
            categories = [
                Category(
                    name=f"Bug Report {uuid.uuid4().hex[:8]}",
                    description="Bug related",
                    created_by=1,
                ),
                Category(
                    name=f"Feature Request {uuid.uuid4().hex[:8]}",
                    description="Feature request",
                    created_by=1,
                ),
            ]
            session.add_all(categories)
            session.commit()
            for cat in categories:
                session.refresh(cat)

            labels = [
                Label(name=f"critical-{uuid.uuid4().hex[:8]}", color="#FF0000", description="Critical issue", created_by=1),
                Label(name=f"high-priority-{uuid.uuid4().hex[:8]}", color="#FFA500", description="High priority", created_by=1),
                Label(name=f"documentation-{uuid.uuid4().hex[:8]}", color="#0000FF", description="Doc related", created_by=1),
            ]
            session.add_all(labels)
            session.commit()
            for label in labels:
                session.refresh(label)

            # 創建工單
            tickets = [
                Ticket(
                    ticket_no=f"TIC-20250101-{uuid.uuid4().hex[:3].upper()}",
                    title="First Ticket",
                    description="First ticket description",
                    status=TicketStatus.DRAFT,
                    priority=TicketPriority.HIGH,
                    visibility=TicketVisibility.INTERNAL,
                    created_by=1,
                    categories=[categories[0]],
                    labels=[labels[0]],
                ),
                Ticket(
                    ticket_no=f"TIC-20250101-{uuid.uuid4().hex[:3].upper()}",
                    title="Second Ticket",
                    description="Second ticket description",
                    status=TicketStatus.OPEN,
                    priority=TicketPriority.MEDIUM,
                    visibility=TicketVisibility.INTERNAL,
                    created_by=1,
                    categories=[categories[1]],
                    labels=[labels[1]],
                ),
                Ticket(
                    ticket_no=f"TIC-20250101-{uuid.uuid4().hex[:3].upper()}",
                    title="Third Ticket",
                    description="Third ticket description",
                    status=TicketStatus.IN_PROGRESS,
                    priority=TicketPriority.LOW,
                    visibility=TicketVisibility.INTERNAL,
                    created_by=2,
                    categories=[categories[0]],
                    labels=[labels[2]],
                ),
            ]
            session.add_all(tickets)
            session.commit()
            for ticket in tickets:
                session.refresh(ticket)
            return tickets
        finally:
            session.close()


# ========== Pytest Configuration ==========


def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line("markers", "integration: Integration test marker")
    config.addinivalue_line("markers", "unit: Unit test marker")
