from datetime import datetime
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.services.category_service import CategoryService

if TYPE_CHECKING:
    from app.repositories.category_repository import CategoryRepository


class TestCategoryService:
    @pytest.fixture
    def mock_repo(self) -> "CategoryRepository":
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_repo: "CategoryRepository") -> CategoryService:
        service = CategoryService()
        service.category_repo = mock_repo
        return service

    @pytest.mark.asyncio
    async def test_create_category_success(self, service: CategoryService, mock_repo: "CategoryRepository"):
        # Arrange
        category_create = CategoryCreate(name="Test Category", description="Test Description")
        user_id = 1
        expected_category = CategoryRead(
            id=1,
            name="Test Category",
            description="Test Description",
            created_at=datetime(2023, 1, 1),
            created_by=user_id,
            updated_at=None,
            updated_by=None,
        )
        mock_repo.get_by_name.return_value = None
        mock_repo.create.return_value = expected_category

        # Act
        result = await service.create_category(category_create, user_id)

        # Assert
        assert result == expected_category
        mock_repo.get_by_name.assert_called_once_with(category_create.name)
        mock_repo.create.assert_called_once_with(category_create, user_id)

    @pytest.mark.asyncio
    async def test_create_category_conflict(self, service: CategoryService, mock_repo: "CategoryRepository"):
        # Arrange
        category_create = CategoryCreate(name="Existing Category", description="Test")
        mock_repo.get_by_name.return_value = MagicMock()  # Simulate existing category

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await service.create_category(category_create)

        assert exc_info.value.status_code == 409
        assert "already exists" in exc_info.value.detail
        mock_repo.get_by_name.assert_called_once_with(category_create.name)
        mock_repo.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_category(self, service: CategoryService, mock_repo: "CategoryRepository"):
        # Arrange
        category_id = 1
        expected_category = CategoryRead(
            id=category_id,
            name="Test Category",
            description="Test",
            created_at=datetime(2023, 1, 1),
            created_by=1,
            updated_at=None,
            updated_by=None,
        )
        mock_repo.get_by_id.return_value = expected_category

        # Act
        result = await service.get_category(category_id)

        # Assert
        assert result == expected_category
        mock_repo.get_by_id.assert_called_once_with(category_id)

    @pytest.mark.asyncio
    async def test_get_categories(self, service: CategoryService, mock_repo: "CategoryRepository"):
        # Arrange
        expected_categories = [
            CategoryRead(
                id=1,
                name="Category 1",
                description="Desc 1",
                created_at=datetime(2023, 1, 1),
                created_by=1,
                updated_at=None,
                updated_by=None,
            ),
            CategoryRead(
                id=2,
                name="Category 2",
                description="Desc 2",
                created_at=datetime(2023, 1, 1),
                created_by=1,
                updated_at=None,
                updated_by=None,
            ),
        ]
        mock_repo.get_all.return_value = expected_categories

        # Act
        result = await service.get_categories()

        # Assert
        assert result == expected_categories
        mock_repo.get_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_category_success(self, service: CategoryService, mock_repo: "CategoryRepository"):
        # Arrange
        category_id = 1
        category_update = CategoryUpdate(name="Updated Name", description="Updated Desc")
        user_id = 1
        expected_category = CategoryRead(
            id=category_id,
            name="Updated Name",
            description="Updated Desc",
            created_at=datetime(2023, 1, 1),
            created_by=1,
            updated_at=datetime(2023, 1, 2),
            updated_by=user_id,
        )
        mock_repo.update.return_value = expected_category

        # Act
        result = await service.update_category(category_id, category_update, user_id)

        # Assert
        assert result == expected_category
        mock_repo.update.assert_called_once_with(category_id, category_update, user_id=user_id)

    @pytest.mark.asyncio
    async def test_update_category_not_found(self, service: CategoryService, mock_repo: "CategoryRepository"):
        # Arrange
        category_id = 999
        category_update = CategoryUpdate(name="Updated Name")
        mock_repo.update.return_value = None

        # Act
        result = await service.update_category(category_id, category_update)

        # Assert
        assert result is None
        mock_repo.update.assert_called_once_with(category_id, category_update, user_id=None)

    @pytest.mark.asyncio
    async def test_soft_delete_category_success(self, service: CategoryService, mock_repo: "CategoryRepository"):
        # Arrange
        category_id = 1
        user_id = 1
        mock_repo.soft_delete.return_value = MagicMock()  # Simulate successful deletion

        # Act
        result = await service.soft_delete_category(category_id, user_id)

        # Assert
        assert result is True
        mock_repo.soft_delete.assert_called_once_with(category_id, user_id)

    @pytest.mark.asyncio
    async def test_soft_delete_category_not_found(self, service: CategoryService, mock_repo: "CategoryRepository"):
        # Arrange
        category_id = 999
        mock_repo.soft_delete.return_value = None

        # Act
        result = await service.soft_delete_category(category_id)

        # Assert
        assert result is False
        mock_repo.soft_delete.assert_called_once_with(category_id, None)
