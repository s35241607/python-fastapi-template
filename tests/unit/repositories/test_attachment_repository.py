#!/usr/bin/env python3
"""
Attachment Repository 的單元測試
測試數據訪問邏輯
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attachment import Attachment
from app.models.enums import AttachmentUsageType
from app.repositories.attachment_repository import AttachmentRepository
from app.schemas.attachment import AttachmentRead, AttachmentUpdate


@pytest.fixture
def mock_session():
    """模擬的數據庫會話"""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def attachment_repository(mock_session):
    """測試用的附件倉庫"""
    repo = AttachmentRepository()
    repo.db = mock_session
    return repo


@pytest.fixture
def sample_attachment():
    """示例附件"""
    return Attachment(
        id=1,
        related_type="tickets",
        related_id=1,
        ticket_id=1,
        usage_type=AttachmentUsageType.GENERAL,
        file_name="test.txt",
        storage_path="uploads/test.txt",
        file_size=12,
        mime_type="text/plain",
        description="Test attachment",
        created_by=1,
        created_at="2023-01-01T00:00:00Z",
        updated_by=1,
        updated_at="2023-01-01T00:00:00Z",
        is_deleted=False,
    )


@pytest.fixture
def sample_attachment_read():
    """示例附件讀取模型"""
    return AttachmentRead(
        id=1,
        related_type="tickets",
        related_id=1,
        usage_type=AttachmentUsageType.GENERAL,
        file_name="test.txt",
        storage_path="uploads/test.txt",
        file_size=12,
        mime_type="text/plain",
        description="Test attachment",
        created_by=1,
        created_at="2023-01-01T00:00:00Z",
    )


class TestAttachmentRepositoryGetByRelated:
    """測試根據關聯取得附件"""

    @pytest.mark.asyncio
    async def test_get_by_related_success(self, attachment_repository, mock_session, sample_attachment, sample_attachment_read):
        """測試成功取得關聯附件"""
        # 模擬查詢結果
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_attachment]
        mock_session.execute.return_value = mock_result

        # 模擬轉換方法
        attachment_repository._convert_many = MagicMock(return_value=[sample_attachment_read])

        result = await attachment_repository.get_by_related("tickets", 1)

        assert len(result) == 1
        assert result[0] == sample_attachment_read
        mock_session.execute.assert_called_once()

        # 驗證 SQL 查詢
        call_args = mock_session.execute.call_args[0][0]
        assert isinstance(call_args, Select)

    @pytest.mark.asyncio
    async def test_get_by_related_empty(self, attachment_repository, mock_session):
        """測試沒有找到附件的情況"""
        # 模擬空結果
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        attachment_repository._convert_many = MagicMock(return_value=[])

        result = await attachment_repository.get_by_related("tickets", 1)

        assert result == []
        mock_session.execute.assert_called_once()


class TestAttachmentRepositoryGetByTicketId:
    """測試根據 ticket ID 取得附件"""

    @pytest.mark.asyncio
    async def test_get_by_ticket_id_success(
        self, attachment_repository, mock_session, sample_attachment, sample_attachment_read
    ):
        """測試成功取得 ticket 附件"""
        # 模擬查詢結果
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_attachment]
        mock_session.execute.return_value = mock_result

        # 模擬轉換方法
        attachment_repository._convert_many = MagicMock(return_value=[sample_attachment_read])

        result = await attachment_repository.get_by_ticket_id(1)

        assert len(result) == 1
        assert result[0] == sample_attachment_read
        mock_session.execute.assert_called_once()

        # 驗證 SQL 查詢
        call_args = mock_session.execute.call_args[0][0]
        assert isinstance(call_args, Select)

    @pytest.mark.asyncio
    async def test_get_by_ticket_id_empty(self, attachment_repository, mock_session):
        """測試 ticket 沒有附件的情況"""
        # 模擬空結果
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        attachment_repository._convert_many = MagicMock(return_value=[])

        result = await attachment_repository.get_by_ticket_id(1)

        assert result == []
        mock_session.execute.assert_called_once()


class TestAttachmentRepositoryInheritance:
    """測試繼承自 BaseRepository 的功能"""

    @pytest.mark.asyncio
    async def test_create_attachment(self, attachment_repository, mock_session, sample_attachment, sample_attachment_read):
        """測試創建附件"""
        # 模擬基類方法
        attachment_repository._convert_one = MagicMock(return_value=sample_attachment_read)

        result = await attachment_repository.create(sample_attachment, 1)

        assert result == sample_attachment_read
        # 驗證調用了基類的 create 方法
        assert attachment_repository._convert_one.called

    @pytest.mark.asyncio
    async def test_get_by_id(self, attachment_repository, mock_session, sample_attachment, sample_attachment_read):
        """測試根據 ID 取得附件"""
        # 模擬基類方法
        attachment_repository._convert_one = MagicMock(return_value=sample_attachment_read)

        result = await attachment_repository.get_by_id(1)

        assert result == sample_attachment_read
        assert attachment_repository._convert_one.called

    @pytest.mark.asyncio
    async def test_update_attachment(self, attachment_repository, mock_session, sample_attachment_read):
        """測試更新附件"""
        update_data = AttachmentUpdate(description="Updated description")

        # 模擬數據庫操作
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_attachment
        mock_session.execute.return_value = mock_result
        mock_session.add.return_value = None
        mock_session.flush.return_value = None
        mock_session.refresh.return_value = None

        # 模擬基類方法
        attachment_repository._convert_one = MagicMock(return_value=sample_attachment_read)

        result = await attachment_repository.update(1, update_data, 1)

        assert result == sample_attachment_read
        assert attachment_repository._convert_one.called

    @pytest.mark.asyncio
    async def test_soft_delete_attachment(self, attachment_repository, mock_session, sample_attachment_read):
        """測試軟刪除附件"""
        # 模擬數據庫操作
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_attachment
        mock_session.execute.return_value = mock_result
        mock_session.add.return_value = None
        mock_session.flush.return_value = None
        mock_session.refresh.return_value = None

        # 模擬轉換方法
        attachment_repository._convert_one = MagicMock(return_value=sample_attachment_read)

        result = await attachment_repository.soft_delete(1, 1)

        assert result == sample_attachment_read
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_attachments(self, attachment_repository, mock_session, sample_attachment, sample_attachment_read):
        """測試取得所有附件"""
        # 模擬數據庫操作
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_attachment]
        mock_session.execute.return_value = mock_result

        # 模擬轉換方法
        attachment_repository._convert_many = MagicMock(return_value=[sample_attachment_read])

        result = await attachment_repository.get_all()

        assert result == [sample_attachment_read]
        assert attachment_repository._convert_many.called
