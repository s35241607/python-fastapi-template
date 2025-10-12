import uuid
from pathlib import Path
from typing import cast

from fastapi import Depends, HTTPException, UploadFile

from app.models.attachment import Attachment
from app.models.enums import AttachmentUsageType
from app.repositories.attachment_repository import AttachmentRepository
from app.schemas.attachment import (
    AttachmentRead,
    AttachmentUpdate,
)


class AttachmentService:
    def __init__(self, attachment_repo: AttachmentRepository = Depends(AttachmentRepository)):
        """Service is constructed with an AttachmentRepository instance.

        Contract:
        - inputs: AttachmentRepository
        - outputs: domain models (Attachment) or primitives
        - error modes: passes through repository exceptions as appropriate
        """
        self.attachment_repo = attachment_repo
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)

        # 文件大小限制 (10MB)
        self.MAX_FILE_SIZE = 10 * 1024 * 1024
        # 允許的文件類型
        self.ALLOWED_MIME_TYPES = {
            # 圖片
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/webp",
            "image/svg+xml",
            # 文檔
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            # 文本
            "text/plain",
            "text/csv",
            "application/json",
            # 壓縮文件
            "application/zip",
            "application/x-rar-compressed",
        }

    def _validate_file(self, file: UploadFile) -> None:
        """驗證上傳的文件"""
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件名不能為空")

        # 檢查文件大小
        file_size = getattr(file, "size", None)
        if file_size and file_size > self.MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"文件大小超過限制 {self.MAX_FILE_SIZE // (1024 * 1024)}MB")

        # 檢查 MIME 類型
        if file.content_type and file.content_type not in self.ALLOWED_MIME_TYPES:
            raise HTTPException(status_code=400, detail=f"不支持的文件類型: {file.content_type}")

    def _validate_related_resource(self, related_type: str, related_id: int) -> None:
        """驗證相關資源是否存在"""
        # 這裡可以添加具體的資源存在性檢查
        # 例如檢查 ticket 是否存在等
        valid_types = ["tickets", "ticket_templates", "categories", "labels"]
        if related_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"無效的相關資源類型: {related_type}")

    async def save_file(self, file: UploadFile, related_type: str, related_id: int, created_by: int) -> AttachmentRead:
        """保存上傳的文件"""
        self._validate_file(file)
        self._validate_related_resource(related_type, related_id)

        # 生成唯一文件名
        file_extension = Path(file.filename).suffix if file.filename else ""
        unique_filename = f"{uuid.uuid4()}{file_extension}"

        # 創建文件路徑
        file_path = self.upload_dir / unique_filename

        # 保存文件
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # 創建附件記錄
        attachment = Attachment(
            related_type=related_type,
            related_id=related_id,
            usage_type=AttachmentUsageType.GENERAL,
            file_name=file.filename or "unnamed",
            storage_path=str(file_path),
            file_size=len(content),
            mime_type=file.content_type or "application/octet-stream",
            created_by=created_by,
        )

        return cast(AttachmentRead, await self.attachment_repo.create(attachment, created_by))

    async def save_file_with_metadata(
        self,
        file: UploadFile,
        related_type: str,
        related_id: int,
        usage_type: AttachmentUsageType,
        description: str | None,
        created_by: int,
    ) -> AttachmentRead:
        """保存上傳的文件並設置 metadata"""
        self._validate_file(file)
        self._validate_related_resource(related_type, related_id)

        # 生成唯一文件名
        file_extension = Path(file.filename).suffix if file.filename else ""
        unique_filename = f"{uuid.uuid4()}{file_extension}"

        # 創建文件路徑
        file_path = self.upload_dir / unique_filename

        # 保存文件
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # 創建附件記錄
        attachment = Attachment(
            related_type=related_type,
            related_id=related_id,
            ticket_id=related_id if related_type == "tickets" else None,
            usage_type=usage_type,
            file_name=file.filename or "unnamed",
            storage_path=str(file_path),
            file_size=len(content),
            mime_type=file.content_type or "application/octet-stream",
            description=description,
            created_by=created_by,
        )

        return cast(AttachmentRead, await self.attachment_repo.create(attachment, created_by))

    async def save_files_with_metadata(
        self,
        files: list[UploadFile],
        related_type: str,
        related_id: int,
        usage_type: AttachmentUsageType,
        description: str | None,
        created_by: int,
    ) -> list[AttachmentRead]:
        """保存多個上傳的文件並設置 metadata"""
        self._validate_related_resource(related_type, related_id)

        attachments: list[AttachmentRead] = []
        for file in files:
            if file.filename:  # 確保文件有文件名
                self._validate_file(file)
                attachment = await self.save_file_with_metadata(
                    file, related_type, related_id, usage_type, description, created_by
                )
                attachments.append(attachment)
        return attachments

    async def get_attachments(self, related_type: str, related_id: int) -> list[AttachmentRead]:
        """取得指定資源的附件"""
        self._validate_related_resource(related_type, related_id)
        return await self.attachment_repo.get_by_related(related_type, related_id)

    async def get_ticket_attachments(self, ticket_id: int) -> list[AttachmentRead]:
        """取得 ticket 的所有附件"""
        return await self.attachment_repo.get_by_ticket_id(ticket_id)

    async def get_attachment(self, attachment_id: int) -> AttachmentRead | None:
        """取得單個附件"""
        return cast(AttachmentRead | None, await self.attachment_repo.get_by_id(attachment_id))

    async def update_attachment(
        self, attachment_id: int, attachment_update: AttachmentUpdate, updated_by: int
    ) -> AttachmentRead | None:
        """更新附件資訊"""
        return cast(AttachmentRead | None, await self.attachment_repo.update(attachment_id, attachment_update, updated_by))

    async def delete_attachment(self, attachment_id: int, deleted_by: int) -> bool:
        """軟刪除附件"""
        result = await self.attachment_repo.soft_delete(attachment_id, deleted_by)
        return result is not None

    async def preupload_file(
        self, file: UploadFile, usage_type: AttachmentUsageType, description: str | None, created_by: int
    ) -> AttachmentRead:
        """預上傳文件，創建未關聯的附件記錄"""
        self._validate_file(file)

        # 生成唯一文件名
        file_extension = Path(file.filename).suffix if file.filename else ""
        unique_filename = f"{uuid.uuid4()}{file_extension}"

        # 創建文件路徑
        file_path = self.upload_dir / unique_filename

        # 保存文件
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # 創建未關聯的附件記錄
        attachment = Attachment(
            related_type=None,  # 未關聯
            related_id=None,  # 未關聯
            ticket_id=None,
            usage_type=usage_type,
            file_name=file.filename or "unnamed",
            storage_path=str(file_path),
            file_size=len(content),
            mime_type=file.content_type or "application/octet-stream",
            description=description,
            created_by=created_by,
        )

        return cast(AttachmentRead, await self.attachment_repo.create(attachment, created_by))

    async def link_attachments_to_resource(
        self, attachment_ids: list[int], related_type: str, related_id: int, updated_by: int
    ) -> list[AttachmentRead]:
        """將預上傳的附件關聯到資源"""
        self._validate_related_resource(related_type, related_id)

        linked_attachments: list[AttachmentRead] = []
        for attachment_id in attachment_ids:
            # 獲取附件
            attachment = await self.attachment_repo.get_by_id(attachment_id)
            if not attachment:
                raise HTTPException(status_code=404, detail=f"附件 {attachment_id} 不存在")

            # 檢查是否已經關聯 (related_type 不為 None 表示已關聯)
            if attachment.related_type is not None:
                raise HTTPException(status_code=400, detail=f"附件 {attachment_id} 已經關聯到其他資源")

            # 更新關聯信息
            update_data = AttachmentUpdate(
                related_type=related_type,
                related_id=related_id,
                ticket_id=related_id if related_type == "tickets" else None,
                description=None,  # 不更新描述
            )
            linked_attachment = await self.attachment_repo.update(attachment_id, update_data, updated_by)
            if linked_attachment:
                linked_attachments.append(linked_attachment)

        return linked_attachments
