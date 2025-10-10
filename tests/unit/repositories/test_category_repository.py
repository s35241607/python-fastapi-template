from datetime import datetime
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate

if TYPE_CHECKING:
    pass


class TestCategoryRepository:
    @pytest.fixture
    def mock_session(self) -> AsyncSession:
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repo(self, mock_session: AsyncSession) -> CategoryRepository:
        return CategoryRepository(session=mock_session)

    @pytest.mark.asyncio
    async def test_get_by_name_found(self, repo: CategoryRepository, mock_session: AsyncSession):
        # Arrange
        name = "Test Category"
        mock_category = Category(
            id=1,
            name=name,
            description="Test",
            created_at=datetime(2023, 1, 1),
            created_by=1,
            updated_at=None,
            updated_by=None,
            is_deleted=False,
        )
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_category
        mock_session.execute.return_value = mock_result

        # Act
        result = await repo.get_by_name(name)

        # Assert
        assert isinstance(result, CategoryRead)
        assert result.name == name
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_name_not_found(self, repo: CategoryRepository, mock_session: AsyncSession):
        # Arrange
        name = "Nonexistent"
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Act
        result = await repo.get_by_name(name)

        # Assert
        assert result is None
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repo: CategoryRepository, mock_session: AsyncSession):
        # Arrange
        category_id = 1
        mock_category = Category(
            id=category_id,
            name="Test",
            description="Test",
            created_at=datetime(2023, 1, 1),
            created_by=1,
            updated_at=None,
            updated_by=None,
            is_deleted=False,
        )
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_category
        mock_session.execute.return_value = mock_result

        # Act
        result = await repo.get_by_id(category_id)

        # Assert
        assert isinstance(result, CategoryRead)
        assert result.id == category_id
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all(self, repo: CategoryRepository, mock_session: AsyncSession):
        # Arrange
        mock_categories = [
            Category(
                id=1,
                name="Category 1",
                description="Desc 1",
                created_at=datetime(2023, 1, 1),
                created_by=1,
                updated_at=None,
                updated_by=None,
                is_deleted=False,
            ),
            Category(
                id=2,
                name="Category 2",
                description="Desc 2",
                created_at=datetime(2023, 1, 1),
                created_by=1,
                updated_at=None,
                updated_by=None,
                is_deleted=False,
            ),
        ]
        mock_result = MagicMock()
        mock_result.scalars().all.return_value = mock_categories
        mock_session.execute.return_value = mock_result

        # Act
        result = await repo.get_all()

        # Assert
        assert len(result) == 2
        assert all(isinstance(cat, CategoryRead) for cat in result)
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_create(self, repo: CategoryRepository, mock_session: AsyncSession):
        # Arrange
        category_create = CategoryCreate(name="New Category", description="New Desc")
        user_id = 1
        mock_category = Category(
            id=1,
            name="New Category",
            description="New Desc",
            created_at=datetime(2023, 1, 1),
            created_by=user_id,
            updated_at=None,
            updated_by=None,
            is_deleted=False,
        )
        mock_session.add.return_value = None
        mock_session.flush.return_value = None
        mock_session.refresh.return_value = None

        # Mock the conversion to return CategoryRead
        repo._convert_one = MagicMock(
            return_value=CategoryRead(
                id=1,
                name="New Category",
                description="New Desc",
                created_at=datetime(2023, 1, 1),
                created_by=user_id,
                updated_at=None,
                updated_by=None,
            )
        )

        # Act
        result = await repo.create(category_create, user_id)

        # Assert
        assert isinstance(result, CategoryRead)
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_success(self, repo: CategoryRepository, mock_session: AsyncSession):
        # Arrange
        category_id = 1
        category_update = CategoryUpdate(name="Updated Name", description="Updated Desc")
        user_id = 1
        mock_category = Category(
            id=category_id,
            name="Old Name",
            description="Old Desc",
            created_at=datetime(2023, 1, 1),
            created_by=1,
            updated_at=None,
            updated_by=None,
            is_deleted=False,
        )

        # Mock _get_model_by_id
        repo._get_model_by_id = AsyncMock(return_value=mock_category)
        mock_session.add.return_value = None
        mock_session.flush.return_value = None
        mock_session.refresh.return_value = None

        repo._convert_required = MagicMock(
            return_value=CategoryRead(
                id=category_id,
                name="Updated Name",
                description="Updated Desc",
                created_at=datetime(2023, 1, 1),
                created_by=1,
                updated_at=datetime(2023, 1, 2),
                updated_by=user_id,
            )
        )

        # Act
        result = await repo.update(category_id, category_update, user_id)

        # Assert
        assert isinstance(result, CategoryRead)
        assert result.name == "Updated Name"
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_not_found(self, repo: CategoryRepository, mock_session: AsyncSession):
        # Arrange
        category_id = 999
        category_update = CategoryUpdate(name="Updated Name")

        # Mock _get_model_by_id to return None
        repo._get_model_by_id = AsyncMock(return_value=None)

        # Act
        result = await repo.update(category_id, category_update)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_soft_delete_success(self, repo: CategoryRepository, mock_session: AsyncSession):
        # Arrange
        category_id = 1
        user_id = 1
        mock_category = Category(
            id=category_id,
            name="Test",
            description="Test",
            created_at=datetime(2023, 1, 1),
            created_by=1,
            updated_at=None,
            updated_by=None,
            is_deleted=False,
        )

        repo._get_model_by_id = AsyncMock(return_value=mock_category)
        mock_session.add.return_value = None
        mock_session.flush.return_value = None
        mock_session.refresh.return_value = None

        repo._convert_required = MagicMock(return_value=mock_category)

        # Act
        result = await repo.soft_delete(category_id, user_id)

        # Assert
        assert result is not None
        assert mock_category.is_deleted is True
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_soft_delete_not_found(self, repo: CategoryRepository, mock_session: AsyncSession):
        # Arrange
        category_id = 999

        repo._get_model_by_id = AsyncMock(return_value=None)

        # Act
        result = await repo.soft_delete(category_id)

        # Assert
        assert result is None
