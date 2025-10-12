#!/usr/bin/env python3
"""
Attachment Service 的單元測試
測試業務邏輯和文件處理
"""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException, UploadFile

from app.models.enums import AttachmentUsageType
from app.repositories.attachment_repository import AttachmentRepository
from app.schemas.attachment import AttachmentRead, AttachmentUpdate
from app.services.attachment_service import AttachmentService


@pytest.fixture
def mock_attachment_repo():
    """模擬的附件倉庫"""
    return AsyncMock(spec=AttachmentRepository)


@pytest.fixture
def attachment_service(mock_attachment_repo):
    """測試用的附件服務"""
    service = AttachmentService()
    service.attachment_repo = mock_attachment_repo
    return service


@pytest.fixture
def temp_upload_dir(attachment_service):
    """臨時上傳目錄"""
    with tempfile.TemporaryDirectory() as temp_dir:
        attachment_service.upload_dir = Path(temp_dir)
        yield temp_dir


@pytest.fixture
def mock_upload_file():
    """模擬上傳文件"""
    file = MagicMock(spec=UploadFile)
    file.filename = "test.txt"
    file.content_type = "text/plain"
    file.size = 100
    file.read = AsyncMock(return_value=b"test content")
    return file


class TestAttachmentServiceValidation:
    """測試文件驗證邏輯"""

    def test_validate_file_valid(self, attachment_service, mock_upload_file):
        """測試有效文件的驗證"""
        # 不應該拋出異常
        attachment_service._validate_file(mock_upload_file)

    def test_validate_file_no_filename(self, attachment_service):
        """測試沒有文件名的文件"""
        file = MagicMock(spec=UploadFile)
        file.filename = None
        file.content_type = "text/plain"

        with pytest.raises(HTTPException) as exc_info:
            attachment_service._validate_file(file)

        assert exc_info.value.status_code == 400
        assert "文件名不能為空" in exc_info.value.detail

    def test_validate_file_too_large(self, attachment_service, mock_upload_file):
        """測試文件過大的情況"""
        mock_upload_file.size = attachment_service.MAX_FILE_SIZE + 1

        with pytest.raises(HTTPException) as exc_info:
            attachment_service._validate_file(mock_upload_file)

        assert exc_info.value.status_code == 400
        assert "文件大小超過限制" in exc_info.value.detail

    def test_validate_file_invalid_mime_type(self, attachment_service, mock_upload_file):
        """測試無效的 MIME 類型"""
        mock_upload_file.content_type = "application/invalid"

        with pytest.raises(HTTPException) as exc_info:
            attachment_service._validate_file(mock_upload_file)

        assert exc_info.value.status_code == 400
        assert "不支持的文件類型" in exc_info.value.detail

    def test_validate_related_resource_valid(self, attachment_service):
        """測試有效的相關資源"""
        # 不應該拋出異常
        attachment_service._validate_related_resource("tickets", 1)

    def test_validate_related_resource_invalid_type(self, attachment_service):
        """測試無效的相關資源類型"""
        with pytest.raises(HTTPException) as exc_info:
            attachment_service._validate_related_resource("invalid_type", 1)

        assert exc_info.value.status_code == 400
        assert "無效的相關資源類型" in exc_info.value.detail


class TestAttachmentServiceSaveFile:
    """測試文件保存功能"""

    @pytest.mark.asyncio
    async def test_save_file_success(self, attachment_service, mock_attachment_repo, temp_upload_dir, mock_upload_file):
        """測試成功保存文件"""
        # 模擬倉庫返回
        expected_attachment = AttachmentRead(
            id=1,
            related_type="tickets",
            related_id=1,
            usage_type=AttachmentUsageType.GENERAL,
            file_name="test.txt",
            storage_path="uploads/test.txt",
            file_size=12,
            mime_type="text/plain",
            created_by=1,
            created_at="2023-01-01T00:00:00Z",
        )
        mock_attachment_repo.create.return_value = expected_attachment

        result = await attachment_service.save_file(mock_upload_file, "tickets", 1, 1)

        assert result == expected_attachment
        mock_attachment_repo.create.assert_called_once()
        call_args = mock_attachment_repo.create.call_args[0][0]
        assert call_args.related_type == "tickets"
        assert call_args.related_id == 1
        assert call_args.usage_type == AttachmentUsageType.GENERAL

    @pytest.mark.asyncio
    async def test_save_file_with_metadata_success(
        self, attachment_service, mock_attachment_repo, temp_upload_dir, mock_upload_file
    ):
        """測試帶 metadata 保存文件"""
        expected_attachment = AttachmentRead(
            id=1,
            related_type="tickets",
            related_id=1,
            usage_type=AttachmentUsageType.INLINE,
            file_name="test.txt",
            storage_path="uploads/test.txt",
            file_size=12,
            mime_type="text/plain",
            description="Test description",
            created_by=1,
            created_at="2023-01-01T00:00:00Z",
        )
        mock_attachment_repo.create.return_value = expected_attachment

        result = await attachment_service.save_file_with_metadata(
            mock_upload_file, "tickets", 1, AttachmentUsageType.INLINE, "Test description", 1
        )

        assert result == expected_attachment
        mock_attachment_repo.create.assert_called_once()
        call_args = mock_attachment_repo.create.call_args[0][0]
        assert call_args.usage_type == AttachmentUsageType.INLINE
        assert call_args.description == "Test description"
        assert call_args.ticket_id == 1  # tickets 類型應該設置 ticket_id

    @pytest.mark.asyncio
    async def test_save_files_with_metadata_success(self, attachment_service, mock_attachment_repo, temp_upload_dir):
        """測試批量保存文件"""
        # 創建多個模擬文件
        files = []
        for i in range(2):
            file = MagicMock(spec=UploadFile)
            file.filename = f"test{i}.txt"
            file.content_type = "text/plain"
            file.size = 100
            file.read = AsyncMock(return_value=b"test content")
            files.append(file)

        expected_attachment = AttachmentRead(
            id=1,
            related_type="tickets",
            related_id=1,
            usage_type=AttachmentUsageType.GENERAL,
            file_name="test0.txt",
            storage_path="uploads/test0.txt",
            file_size=12,
            mime_type="text/plain",
            created_by=1,
            created_at="2023-01-01T00:00:00Z",
        )
        mock_attachment_repo.create.return_value = expected_attachment

        result = await attachment_service.save_files_with_metadata(
            files, "tickets", 1, AttachmentUsageType.GENERAL, "Test description", 1
        )

        assert len(result) == 2
        assert mock_attachment_repo.create.call_count == 2


class TestAttachmentServicePreupload:
    """測試預上傳功能"""

    @pytest.mark.asyncio
    async def test_preupload_file_success(self, attachment_service, mock_attachment_repo, temp_upload_dir, mock_upload_file):
        """測試成功預上傳文件"""
        expected_attachment = AttachmentRead(
            id=1,
            related_type=None,
            related_id=None,
            usage_type=AttachmentUsageType.GENERAL,
            file_name="test.txt",
            storage_path="uploads/test.txt",
            file_size=12,
            mime_type="text/plain",
            description="Test preupload",
            created_by=1,
            created_at="2023-01-01T00:00:00Z",
        )
        mock_attachment_repo.create.return_value = expected_attachment

        result = await attachment_service.preupload_file(mock_upload_file, AttachmentUsageType.GENERAL, "Test preupload", 1)

        assert result == expected_attachment
        mock_attachment_repo.create.assert_called_once()
        call_args = mock_attachment_repo.create.call_args[0][0]
        assert call_args.related_type is None
        assert call_args.related_id is None
        assert call_args.ticket_id is None


class TestAttachmentServiceLink:
    """測試附件關聯功能"""

    @pytest.mark.asyncio
    async def test_link_attachments_success(self, attachment_service, mock_attachment_repo):
        """測試成功關聯附件"""
        # 模擬未關聯的附件
        attachment = AttachmentRead(
            id=1,
            related_type=None,
            related_id=None,
            usage_type=AttachmentUsageType.GENERAL,
            file_name="test.txt",
            storage_path="uploads/test.txt",
            file_size=12,
            mime_type="text/plain",
            created_by=1,
            created_at="2023-01-01T00:00:00Z",
        )
        mock_attachment_repo.get_by_id.return_value = attachment

        # 模擬更新後的附件
        updated_attachment = AttachmentRead(
            id=1,
            related_type="tickets",
            related_id=1,
            usage_type=AttachmentUsageType.GENERAL,
            file_name="test.txt",
            storage_path="uploads/test.txt",
            file_size=12,
            mime_type="text/plain",
            created_by=1,
            created_at="2023-01-01T00:00:00Z",
        )
        mock_attachment_repo.update.return_value = updated_attachment

        result = await attachment_service.link_attachments_to_resource([1], "tickets", 1, 1)

        assert len(result) == 1
        assert result[0] == updated_attachment
        mock_attachment_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_link_attachments_already_linked(self, attachment_service, mock_attachment_repo):
        """測試關聯已經關聯的附件"""
        # 模擬已經關聯的附件
        attachment = AttachmentRead(
            id=1,
            related_type="tickets",
            related_id=2,  # 已經關聯到其他資源
            usage_type=AttachmentUsageType.GENERAL,
            file_name="test.txt",
            storage_path="uploads/test.txt",
            file_size=12,
            mime_type="text/plain",
            created_by=1,
            created_at="2023-01-01T00:00:00Z",
        )
        mock_attachment_repo.get_by_id.return_value = attachment

        with pytest.raises(HTTPException) as exc_info:
            await attachment_service.link_attachments_to_resource([1], "tickets", 1, 1)

        assert exc_info.value.status_code == 400
        assert "已經關聯到其他資源" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_link_attachments_not_found(self, attachment_service, mock_attachment_repo):
        """測試關聯不存在的附件"""
        mock_attachment_repo.get_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await attachment_service.link_attachments_to_resource([999], "tickets", 1, 1)

        assert exc_info.value.status_code == 404
        assert "不存在" in exc_info.value.detail


class TestAttachmentServiceGet:
    """測試附件查詢功能"""

    @pytest.mark.asyncio
    async def test_get_attachments(self, attachment_service, mock_attachment_repo):
        """測試取得資源附件"""
        expected_attachments = [
            AttachmentRead(
                id=1,
                related_type="tickets",
                related_id=1,
                usage_type=AttachmentUsageType.GENERAL,
                file_name="test.txt",
                storage_path="uploads/test.txt",
                file_size=12,
                mime_type="text/plain",
                created_by=1,
                created_at="2023-01-01T00:00:00Z",
            )
        ]
        mock_attachment_repo.get_by_related.return_value = expected_attachments

        result = await attachment_service.get_attachments("tickets", 1)

        assert result == expected_attachments
        mock_attachment_repo.get_by_related.assert_called_once_with("tickets", 1)

    @pytest.mark.asyncio
    async def test_get_ticket_attachments(self, attachment_service, mock_attachment_repo):
        """測試取得 ticket 附件"""
        expected_attachments = [
            AttachmentRead(
                id=1,
                related_type="tickets",
                related_id=1,
                usage_type=AttachmentUsageType.GENERAL,
                file_name="test.txt",
                storage_path="uploads/test.txt",
                file_size=12,
                mime_type="text/plain",
                created_by=1,
                created_at="2023-01-01T00:00:00Z",
            )
        ]
        mock_attachment_repo.get_by_ticket_id.return_value = expected_attachments

        result = await attachment_service.get_ticket_attachments(1)

        assert result == expected_attachments
        mock_attachment_repo.get_by_ticket_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_attachment(self, attachment_service, mock_attachment_repo):
        """測試取得單個附件"""
        expected_attachment = AttachmentRead(
            id=1,
            related_type="tickets",
            related_id=1,
            usage_type=AttachmentUsageType.GENERAL,
            file_name="test.txt",
            storage_path="uploads/test.txt",
            file_size=12,
            mime_type="text/plain",
            created_by=1,
            created_at="2023-01-01T00:00:00Z",
        )
        mock_attachment_repo.get_by_id.return_value = expected_attachment

        result = await attachment_service.get_attachment(1)

        assert result == expected_attachment
        mock_attachment_repo.get_by_id.assert_called_once_with(1)


class TestAttachmentServiceUpdate:
    """測試附件更新功能"""

    @pytest.mark.asyncio
    async def test_update_attachment_success(self, attachment_service, mock_attachment_repo):
        """測試成功更新附件"""
        update_data = AttachmentUpdate(description="Updated description")
        expected_attachment = AttachmentRead(
            id=1,
            related_type="tickets",
            related_id=1,
            usage_type=AttachmentUsageType.GENERAL,
            file_name="test.txt",
            storage_path="uploads/test.txt",
            file_size=12,
            mime_type="text/plain",
            description="Updated description",
            created_by=1,
            created_at="2023-01-01T00:00:00Z",
        )
        mock_attachment_repo.update.return_value = expected_attachment

        result = await attachment_service.update_attachment(1, update_data, 1)

        assert result == expected_attachment
        mock_attachment_repo.update.assert_called_once_with(1, update_data, 1)


class TestAttachmentServiceDelete:
    """測試附件刪除功能"""

    @pytest.mark.asyncio
    async def test_delete_attachment_success(self, attachment_service, mock_attachment_repo):
        """測試成功刪除附件"""
        mock_attachment_repo.soft_delete.return_value = True

        result = await attachment_service.delete_attachment(1, 1)

        assert result is True
        mock_attachment_repo.soft_delete.assert_called_once_with(1, 1)

    @pytest.mark.asyncio
    async def test_delete_attachment_not_found(self, attachment_service, mock_attachment_repo):
        """測試刪除不存在的附件"""
        mock_attachment_repo.soft_delete.return_value = None

        result = await attachment_service.delete_attachment(1, 1)

        assert result is False
        mock_attachment_repo.soft_delete.assert_called_once_with(1, 1)
