"""
MinIO 檔案上傳功能使用範例

這個檔案展示了如何使用新建立的檔案上傳功能，
包括一般附件上傳和富文本編輯器的圖片上傳。
"""

import asyncio
import aiofiles
from fastapi import UploadFile
from io import BytesIO

from app.config import settings
from app.database import get_db
from app.repositories.attachment_repository import AttachmentRepository
from app.services.attachment_service import AttachmentService
from app.services.minio_service import minio_service


async def example_upload_file():
    """範例：上傳一般檔案"""
    
    # 模擬上傳檔案
    test_content = b"This is a test file content"
    
    # 建立模擬的 UploadFile
    class MockUploadFile:
        def __init__(self, filename: str, content: bytes, content_type: str):
            self.filename = filename
            self.content = content
            self.content_type = content_type
            self._file = BytesIO(content)
        
        async def read(self) -> bytes:
            return self.content
    
    mock_file = MockUploadFile(
        filename="test_document.txt",
        content=test_content,
        content_type="text/plain"
    )
    
    # 取得資料庫 session
    async for db in get_db():
        # 建立服務
        attachment_repository = AttachmentRepository(db)
        attachment_service = AttachmentService(attachment_repository)
        
        # 上傳檔案
        success, message, attachment = await attachment_service.upload_file(
            file=mock_file,
            user_id=1,
            ticket_id=1,
            usage_type="attachment",
            description="測試文件上傳"
        )
        
        if success:
            print(f"✅ 檔案上傳成功: {message}")
            print(f"📁 檔案資訊: {attachment.file_name} ({attachment.file_size} bytes)")
            print(f"🔗 下載連結: {attachment.file_url}")
        else:
            print(f"❌ 檔案上傳失敗: {message}")
        
        break


async def example_upload_image():
    """範例：上傳圖片 (富文本編輯器用)"""
    
    # 讀取真實圖片檔案 (如果存在)
    image_path = "test_image.jpg"  # 請替換為實際的圖片路徑
    
    try:
        async with aiofiles.open(image_path, "rb") as f:
            image_content = await f.read()
    except FileNotFoundError:
        # 如果沒有測試圖片，建立模擬內容
        print("📝 使用模擬圖片內容 (請提供真實圖片檔案以測試完整功能)")
        image_content = b"fake image content"
    
    class MockUploadFile:
        def __init__(self, filename: str, content: bytes, content_type: str):
            self.filename = filename
            self.content = content
            self.content_type = content_type
        
        async def read(self) -> bytes:
            return self.content
    
    mock_image = MockUploadFile(
        filename="test_image.jpg",
        content=image_content,
        content_type="image/jpeg"
    )
    
    async for db in get_db():
        attachment_repository = AttachmentRepository(db)
        attachment_service = AttachmentService(attachment_repository)
        
        success, message, attachment = await attachment_service.upload_file(
            file=mock_image,
            user_id=1,
            ticket_id=1,
            usage_type="inline_image",
            description="富文本編輯器內嵌圖片"
        )
        
        if success:
            print(f"✅ 圖片上傳成功: {message}")
            print(f"🖼️ 圖片資訊: {attachment.file_name}")
            if attachment.image_width and attachment.image_height:
                print(f"📏 圖片尺寸: {attachment.image_width} x {attachment.image_height}")
            print(f"🔗 圖片連結: {attachment.file_url}")
        else:
            print(f"❌ 圖片上傳失敗: {message}")
        
        break


async def example_minio_service():
    """範例：直接使用 MinIO 服務"""
    
    print("\n🔧 測試 MinIO 服務...")
    
    # 測試上傳
    test_content = b"Direct MinIO service test content"
    success, message, file_info = await minio_service.upload_file(
        file_content=test_content,
        filename="direct_test.txt",
        is_image=False,
        folder="test"
    )
    
    if success:
        print(f"✅ MinIO 直接上傳成功: {message}")
        print(f"📁 檔案資訊: {file_info}")
        
        # 測試獲取 URL
        file_url = minio_service.get_file_url(
            bucket=file_info["bucket"],
            file_path=file_info["file_path"]
        )
        print(f"🔗 檔案 URL: {file_url}")
        
        # 測試下載
        success, content, metadata = await minio_service.download_file(
            bucket=file_info["bucket"],
            file_path=file_info["file_path"]
        )
        
        if success:
            print(f"✅ 檔案下載成功，內容長度: {len(content)}")
            print(f"📋 元資料: {metadata}")
        else:
            print("❌ 檔案下載失敗")
        
        # 測試刪除
        success, message = await minio_service.delete_file(
            bucket=file_info["bucket"],
            file_path=file_info["file_path"]
        )
        print(f"🗑️ 檔案刪除: {message}")
        
    else:
        print(f"❌ MinIO 直接上傳失敗: {message}")


async def main():
    """主函式"""
    print("🚀 MinIO 檔案上傳功能測試")
    print("=" * 50)
    
    print("\n📤 測試一般檔案上傳...")
    await example_upload_file()
    
    print("\n🖼️ 測試圖片上傳...")
    await example_upload_image()
    
    print("\n🔧 測試 MinIO 服務...")
    await example_minio_service()
    
    print("\n✨ 測試完成！")


if __name__ == "__main__":
    # 執行範例
    asyncio.run(main())


"""
API 使用範例 (HTTP 請求)

1. 上傳一般檔案:
POST /api/v1/attachments/upload
Content-Type: multipart/form-data

file: [檔案]
ticket_id: 1
usage_type: attachment
description: "這是一個測試附件"

2. 上傳圖片 (富文本編輯器):
POST /api/v1/attachments/upload/image
Content-Type: multipart/form-data

file: [圖片檔案]
ticket_id: 1
description: "內嵌圖片"

3. 獲取附件資訊:
GET /api/v1/attachments/{attachment_id}

4. 獲取檔案下載 URL:
GET /api/v1/attachments/{attachment_id}/url

5. 直接下載檔案:
GET /api/v1/attachments/{attachment_id}/download

6. 獲取 ticket 的附件列表:
GET /api/v1/attachments/ticket/{ticket_id}/attachments

7. 獲取 ticket 的圖片列表:
GET /api/v1/attachments/ticket/{ticket_id}/images

8. 更新附件資訊:
PUT /api/v1/attachments/{attachment_id}
Content-Type: application/json

{
    "file_name": "new_name.txt",
    "description": "更新的描述"
}

9. 刪除附件:
DELETE /api/v1/attachments/{attachment_id}
"""


"""
Production 環境設定建議

1. 環境變數設定 (.env):
MINIO_ENDPOINT="your-minio-server.com"
MINIO_ACCESS_KEY="your-access-key"
MINIO_SECRET_KEY="your-secret-key"
MINIO_SECURE=true
MINIO_REGION="us-east-1"

# 如果使用 AWS S3
MINIO_ENDPOINT="s3.amazonaws.com"

# 如果使用其他 S3 相容服務
MINIO_ENDPOINT="your-s3-compatible-service.com"

2. CDN 設定:
CDN_DOMAIN="https://cdn.yourdomain.com"

3. 檔案大小限制:
MAX_FILE_SIZE=52428800  # 50MB
MAX_IMAGE_SIZE=10485760  # 10MB

4. 安全設定:
- 確保 MinIO 伺服器啟用 HTTPS
- 設定適當的 CORS 政策
- 使用強密碼和適當的存取控制
- 定期輪換存取金鑰
- 設定適當的儲存桶政策

5. 監控和備份:
- 設定檔案上傳和下載的監控
- 定期備份重要檔案
- 監控儲存空間使用情況
- 設定日誌記錄

6. 效能最佳化:
- 使用 CDN 加速檔案存取
- 設定適當的快取策略
- 考慮使用多部分上傳處理大檔案
- 定期清理孤立的檔案
"""