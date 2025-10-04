from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate


class TestCategoryRepository:
    @pytest.fixture
    def mock_session(self) -> AsyncMock:
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def repo(self, mock_session: AsyncSession) -> CategoryRepository:
        # Create a repository instance with auto_convert=False for unit testing
        # This ensures the repository methods return raw SQLAlchemy models,
        # which is easier to mock and assert against.
        repo = CategoryRepository(session=mock_session)
        repo._auto_convert = False
        return repo

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repo: CategoryRepository, mock_session: AsyncSession):
        # Arrange
        category_id = 1
        mock_category = Category(id=category_id, name="Test")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_category
        mock_session.execute.return_value = mock_result

        # Act
        result = await repo.get_by_id(category_id)

        # Assert
        mock_session.execute.assert_called_once()
        assert result is not None
        assert result.id == category_id
        assert result.name == "Test"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repo: CategoryRepository, mock_session: AsyncSession):
        # Arrange
        category_id = 1
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        # Act
        result = await repo.get_by_id(category_id)

        # Assert
        mock_session.execute.assert_called_once()
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_ids(self, repo: CategoryRepository, mock_session: AsyncSession):
        # Arrange
        category_ids = [1, 2]
        mock_categories = [
            Category(id=1, name="Cat 1"),
            Category(id=2, name="Cat 2"),
        ]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_categories
        mock_session.execute.return_value = mock_result

        # Act
        result = await repo.get_by_ids(category_ids)

        # Assert
        mock_session.execute.assert_called_once()
        assert len(result) == 2
        assert result[0].id == 1

    @pytest.mark.asyncio
    async def test_get_all(self, repo: CategoryRepository, mock_session: AsyncSession):
        # Arrange
        mock_categories = [
            Category(id=1, name="Cat 1"),
            Category(id=2, name="Cat 2"),
        ]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_categories
        mock_session.execute.return_value = mock_result

        # Act
        result = await repo.get_all()

        # Assert
        mock_session.execute.assert_called_once()
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_create(self, repo: CategoryRepository, mock_session: AsyncSession):
        # Arrange
        category_create = CategoryCreate(name="New Category", description="New Desc")
        user_id = 1

        # Act
        # The create method now returns the raw model instance
        result = await repo.create(category_create, user_id)

        # Assert
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()

        # The repository should return the raw model, not a Pydantic schema
        assert isinstance(result, Category)
        assert result.name == category_create.name
        assert result.created_by == user_id

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
        )
        repo._get_model_by_id = AsyncMock(return_value=mock_category)

        # Act
        result = await repo.update(category_id, category_update, user_id)

        # Assert
        repo._get_model_by_id.assert_called_once_with(category_id, include_deleted=True)
        mock_session.add.assert_called_once_with(mock_category)
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once_with(mock_category)

        # Check that the attributes were updated correctly on the model
        assert isinstance(result, Category)
        assert result.name == "Updated Name"
        assert result.updated_by == user_id
        assert result.updated_at is not None

    @pytest.mark.asyncio
    async def test_soft_delete_success(self, repo: CategoryRepository, mock_session: AsyncSession):
        # Arrange
        category_id = 1
        user_id = 1
        mock_category = Category(id=category_id, name="To Be Deleted", created_at=datetime.now(UTC))
        repo._get_model_by_id = AsyncMock(return_value=mock_category)

        # Act
        result = await repo.soft_delete(category_id, user_id)

        # Assert
        repo._get_model_by_id.assert_called_once_with(category_id)
        mock_session.add.assert_called_once_with(mock_category)
        mock_session.flush.assert_called_once()
        assert mock_category.deleted_at is not None
        assert mock_category.deleted_by == user_id
        assert isinstance(result, Category)