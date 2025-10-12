from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from app.auth.dependencies import get_user_id_from_jwt
from app.models.enums import AttachmentUsageType
from app.schemas.attachment import (
    AttachmentListRequest,
    AttachmentListResponse,
    AttachmentRead,
    AttachmentUpdate,
    AttachmentUploadResponse,
    LinkAttachmentsRequest,
    LinkAttachmentsResponse,
    MultipleAttachmentUploadResponse,
    RichTextImageUploadResponse,
    UnifiedUploadRequest,
)
from app.services.attachment_service import AttachmentService

router = APIRouter()


@router.post(
    "/upload",
    response_model=AttachmentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_attachment(
    file: UploadFile = File(...),
    request: UnifiedUploadRequest = Depends(),
    attachment_service: AttachmentService = Depends(AttachmentService),
    current_user_id: int = Depends(get_user_id_from_jwt),
) -> AttachmentUploadResponse:
    """上傳單個附件並關聯到資源"""
    # 驗證 usage_type
    usage_enum = AttachmentUsageType(request.usage_type.lower())

    if not request.related_type or not request.related_id:
        raise HTTPException(status_code=400, detail="上傳需要提供 related_type 和 related_id")

    # 保存文件並設置 metadata
    attachment = await attachment_service.save_file_with_metadata(
        file, request.related_type, request.related_id, usage_enum, request.description, current_user_id
    )

    # 生成訪問 URL
    upload_url = f"/uploads/{Path(attachment.storage_path).name}"
    return AttachmentUploadResponse(attachment=attachment, upload_url=upload_url)


@router.post(
    "/upload/batch",
    response_model=MultipleAttachmentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_attachments_batch(
    files: list[UploadFile] = File(...),
    request: UnifiedUploadRequest = Depends(),
    attachment_service: AttachmentService = Depends(AttachmentService),
    current_user_id: int = Depends(get_user_id_from_jwt),
) -> MultipleAttachmentUploadResponse:
    """批量上傳附件"""
    # 驗證 usage_type
    usage_enum = AttachmentUsageType(request.usage_type.lower())

    if not request.related_type or not request.related_id:
        raise HTTPException(status_code=400, detail="批量上傳需要提供 related_type 和 related_id")

    # 保存文件
    attachments = await attachment_service.save_files_with_metadata(
        files, request.related_type, request.related_id, usage_enum, request.description, current_user_id
    )
    return MultipleAttachmentUploadResponse(attachments=attachments, total_uploaded=len(attachments))


@router.post(
    "/upload/preupload",
    response_model=AttachmentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_attachment_preupload(
    file: UploadFile = File(...),
    request: UnifiedUploadRequest = Depends(),
    attachment_service: AttachmentService = Depends(AttachmentService),
    current_user_id: int = Depends(get_user_id_from_jwt),
) -> AttachmentUploadResponse:
    """預上傳附件（不關聯到資源）"""
    # 驗證 usage_type
    usage_enum = AttachmentUsageType(request.usage_type.lower())

    # 預上傳文件
    attachment = await attachment_service.preupload_file(file, usage_enum, request.description, current_user_id)

    # 生成訪問 URL
    upload_url = f"/uploads/{Path(attachment.storage_path).name}"
    return AttachmentUploadResponse(attachment=attachment, upload_url=upload_url)


@router.post(
    "/upload/rich-text-image",
    response_model=RichTextImageUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_rich_text_image(
    file: UploadFile = File(...),
    request: UnifiedUploadRequest = Depends(),
    attachment_service: AttachmentService = Depends(AttachmentService),
    current_user_id: int = Depends(get_user_id_from_jwt),
) -> RichTextImageUploadResponse:
    """上傳富文本圖片"""
    if not request.related_type or not request.related_id:
        raise HTTPException(status_code=400, detail="富文本圖片上傳需要提供 related_type 和 related_id")

    # 保存文件為 inline 類型
    attachment = await attachment_service.save_file_with_metadata(
        file, request.related_type, request.related_id, AttachmentUsageType.INLINE, request.alt_text, current_user_id
    )

    # 生成 Markdown 語法，使用 download API
    download_url = f"/api/v1/attachments/{attachment.id}/download"
    markdown_syntax = f"![{request.alt_text or attachment.file_name}]({download_url})"

    return RichTextImageUploadResponse(
        attachment=attachment,
        attachment_id=attachment.id,
        markdown_syntax=markdown_syntax
    )


@router.get("/{attachment_id}", response_model=AttachmentRead)
async def get_attachment(
    attachment_id: int,
    attachment_service: AttachmentService = Depends(AttachmentService),
    current_user_id: int = Depends(get_user_id_from_jwt),
) -> AttachmentRead:
    """取得單個附件資訊"""
    # TODO: 添加權限檢查
    attachment = await attachment_service.get_attachment(attachment_id)
    if not attachment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="附件不存在")

    return attachment


@router.get("/", response_model=AttachmentListResponse)
async def get_attachments(
    request: AttachmentListRequest = Depends(),
    attachment_service: AttachmentService = Depends(AttachmentService),
    current_user_id: int = Depends(get_user_id_from_jwt),
) -> AttachmentListResponse:
    """取得指定資源的附件列表"""
    # 獲取附件
    attachments = await attachment_service.get_attachments(request.related_type, request.related_id)

    # 如果指定了 usage_type，進行過濾
    if request.usage_type:
        usage_enum = AttachmentUsageType(request.usage_type.lower())
        attachments = [att for att in attachments if att.usage_type == usage_enum]

    return AttachmentListResponse(attachments=attachments, total=len(attachments))


@router.put("/{attachment_id}", response_model=AttachmentRead)
async def update_attachment(
    attachment_id: int,
    attachment_update: AttachmentUpdate,
    attachment_service: AttachmentService = Depends(AttachmentService),
    current_user_id: int = Depends(get_user_id_from_jwt),
) -> AttachmentRead:
    """更新附件資訊"""
    # TODO: 添加權限檢查 (只有創建者可以更新)
    attachment = await attachment_service.update_attachment(attachment_id, attachment_update, current_user_id)
    if not attachment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="附件不存在")

    return attachment


@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(
    attachment_id: int,
    attachment_service: AttachmentService = Depends(AttachmentService),
    current_user_id: int = Depends(get_user_id_from_jwt),
) -> None:
    """軟刪除附件"""
    # TODO: 添加權限檢查 (只有創建者可以刪除)
    success = await attachment_service.delete_attachment(attachment_id, current_user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="附件不存在")


@router.post("/link", response_model=LinkAttachmentsResponse, status_code=status.HTTP_200_OK)
async def link_attachments(
    request: LinkAttachmentsRequest,
    attachment_service: AttachmentService = Depends(AttachmentService),
    current_user_id: int = Depends(get_user_id_from_jwt),
) -> LinkAttachmentsResponse:
    """將預上傳的附件關聯到資源"""
    # 關聯附件
    linked_attachments = await attachment_service.link_attachments_to_resource(
        request.attachment_ids, request.related_type, request.related_id, current_user_id
    )

    return LinkAttachmentsResponse(linked_attachments=linked_attachments, total_linked=len(linked_attachments))


@router.get("/{attachment_id}/download")
async def download_attachment(
    attachment_id: int,
    attachment_service: AttachmentService = Depends(AttachmentService),
    current_user_id: int = Depends(get_user_id_from_jwt),
) -> FileResponse:
    """下載附件檔案"""
    # TODO: 添加權限檢查
    attachment = await attachment_service.get_attachment(attachment_id)
    if not attachment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="附件不存在")

    # 檢查檔案是否存在
    file_path = Path(attachment.storage_path)
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="檔案不存在")

    # 返回檔案
    return FileResponse(
        path=file_path,
        filename=attachment.file_name,
        media_type=attachment.mime_type,
    )
