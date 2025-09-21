"""
MinIO 檔案儲存服務
提供檔案上傳、下載、刪除等功能，適用於 production 環境
"""

import asyncio
import io
import uuid
from datetime import datetime, timedelta
from typing import BinaryIO, Optional

try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

from minio import Minio
from minio.error import S3Error
from PIL import Image

from app.config import settings


class MinIOService:
    """MinIO 檔案儲存服務"""

    def __init__(self):
        """初始化 MinIO 客戶端"""
        # 只在 region 不為空時才傳遞該參數
        client_config = {
            "endpoint": settings.minio_endpoint,
            "access_key": settings.minio_access_key,
            "secret_key": settings.minio_secret_key,
            "secure": settings.minio_secure,
        }
        
        if settings.minio_region:
            client_config["region"] = settings.minio_region
        
        self.client = Minio(**client_config)
        self._buckets_initialized = False

    async def _ensure_buckets_exist(self) -> None:
        """確保所有需要的儲存桶都存在"""
        if self._buckets_initialized:
            return
            
        buckets = [
            settings.minio_bucket_attachments,
            settings.minio_bucket_images,
        ]
        
        for bucket in buckets:
            try:
                if not self.client.bucket_exists(bucket):
                    self.client.make_bucket(bucket, location=settings.minio_region)
                    print(f"✅ 建立儲存桶: {bucket}")
                    
                    # 設定儲存桶策略 (允許讀取)
                    policy = {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Principal": {"AWS": "*"},
                                "Action": ["s3:GetObject"],
                                "Resource": [f"arn:aws:s3:::{bucket}/*"]
                            }
                        ]
                    }
                    
                    import json
                    self.client.set_bucket_policy(bucket, json.dumps(policy))
                else:
                    print(f"📦 儲存桶已存在: {bucket}")
                    
            except S3Error as e:
                print(f"❌ 建立儲存桶 {bucket} 時發生錯誤: {e}")
                # 不要因為策略設定失敗就停止
                continue
        
        self._buckets_initialized = True

    def _get_file_type(self, file_content: bytes, filename: str) -> str:
        """檢測檔案類型"""
        # 首先嘗試使用 python-magic (如果可用)
        if MAGIC_AVAILABLE:
            try:
                mime_type = magic.from_buffer(file_content, mime=True)
                return mime_type
            except Exception:
                pass  # 如果失敗，使用副檔名檢測
        
        # 備用方案：根據副檔名推測
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        mime_type_map = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'svg': 'image/svg+xml',
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'xls': 'application/vnd.ms-excel',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'txt': 'text/plain',
            'csv': 'text/csv',
            'zip': 'application/zip',
            'rar': 'application/x-rar-compressed',
            'json': 'application/json',
            'xml': 'application/xml',
            'html': 'text/html',
            'css': 'text/css',
            'js': 'application/javascript',
            'mp4': 'video/mp4',
            'avi': 'video/x-msvideo',
            'mov': 'video/quicktime',
            'mp3': 'audio/mpeg',
            'wav': 'audio/wav',
        }
        return mime_type_map.get(ext, 'application/octet-stream')

    def _validate_file(self, file_content: bytes, filename: str, is_image: bool = False) -> tuple[bool, str]:
        """驗證檔案"""
        # 檢查檔案大小
        file_size = len(file_content)
        max_size = settings.max_image_size if is_image else settings.max_file_size
        
        if file_size > max_size:
            max_size_mb = max_size / (1024 * 1024)
            return False, f"檔案大小超過限制 ({max_size_mb:.1f}MB)"
        
        # 檢查檔案類型
        mime_type = self._get_file_type(file_content, filename)
        allowed_types = settings.allowed_image_types if is_image else settings.allowed_file_types
        
        if mime_type not in allowed_types:
            return False, f"不支援的檔案類型: {mime_type}"
        
        # 如果是圖片，額外驗證
        if is_image:
            try:
                img = Image.open(io.BytesIO(file_content))
                img.verify()
            except Exception:
                return False, "無效的圖片檔案"
        
        return True, ""

    def _generate_file_path(self, filename: str, folder: str = "") -> str:
        """生成檔案路徑"""
        # 使用 UUID 避免檔名衝突
        file_ext = filename.split('.')[-1] if '.' in filename else ''
        unique_filename = f"{uuid.uuid4()}.{file_ext}" if file_ext else str(uuid.uuid4())
        
        # 按日期組織檔案
        date_path = datetime.now().strftime("%Y/%m/%d")
        
        if folder:
            return f"{folder}/{date_path}/{unique_filename}"
        else:
            return f"{date_path}/{unique_filename}"

    async def upload_file(
        self,
        file_content: bytes,
        filename: str,
        is_image: bool = False,
        folder: str = "",
        metadata: Optional[dict] = None
    ) -> tuple[bool, str, dict]:
        """
        上傳檔案到 MinIO
        
        Args:
            file_content: 檔案內容
            filename: 原始檔名
            is_image: 是否為圖片檔案
            folder: 資料夾名稱
            metadata: 額外的中繼資料
            
        Returns:
            (success, message, file_info)
        """
        try:
            # 確保儲存桶存在
            await self._ensure_buckets_exist()
            
            # 驗證檔案
            is_valid, error_msg = self._validate_file(file_content, filename, is_image)
            if not is_valid:
                return False, error_msg, {}
            
            # 決定儲存桶
            bucket = settings.minio_bucket_images if is_image else settings.minio_bucket_attachments
            
            # 生成檔案路徑
            file_path = self._generate_file_path(filename, folder)
            
            # 取得內容類型
            content_type = self._get_file_type(file_content, filename)
            
            # 準備中繼資料（不包含 content-type）
            file_metadata = {
                "original-filename": filename,
                "upload-time": datetime.now().isoformat(),
                "file-size": str(len(file_content)),
            }
            
            if metadata:
                file_metadata.update(metadata)
            
            # 上傳檔案
            file_stream = io.BytesIO(file_content)
            self.client.put_object(
                bucket_name=bucket,
                object_name=file_path,
                data=file_stream,
                length=len(file_content),
                content_type=content_type,  # 作為參數而不是 metadata
                metadata=file_metadata,
            )
            
            # 返回檔案資訊
            file_info = {
                "file_path": file_path,
                "bucket": bucket,
                "file_size": len(file_content),
                "mime_type": content_type,  # 使用之前取得的 content_type
                "url": self.get_file_url(bucket, file_path),
            }
            
            return True, "檔案上傳成功", file_info
            
        except Exception as e:
            return False, f"檔案上傳失敗: {str(e)}", {}

    def get_file_url(self, bucket: str, file_path: str, expiry: Optional[int] = None) -> str:
        """
        獲取檔案的預簽名 URL
        
        Args:
            bucket: 儲存桶名稱
            file_path: 檔案路徑
            expiry: URL 有效期限 (秒)
            
        Returns:
            預簽名 URL
        """
        try:
            if expiry is None:
                expiry = settings.file_url_expiry
            
            url = self.client.presigned_get_object(
                bucket_name=bucket,
                object_name=file_path,
                expires=timedelta(seconds=expiry)
            )
            
            # 如果設定了 CDN 域名，替換 URL
            if settings.cdn_domain:
                url = url.replace(f"http{'s' if settings.minio_secure else ''}://{settings.minio_endpoint}", settings.cdn_domain)
            
            return url
            
        except Exception as e:
            print(f"Error generating file URL: {e}")
            return ""

    async def download_file(self, bucket: str, file_path: str) -> tuple[bool, bytes, dict]:
        """
        下載檔案
        
        Args:
            bucket: 儲存桶名稱
            file_path: 檔案路徑
            
        Returns:
            (success, file_content, metadata)
        """
        try:
            response = self.client.get_object(bucket, file_path)
            file_content = response.read()
            
            # 獲取中繼資料
            metadata = response.metadata if hasattr(response, 'metadata') else {}
            
            return True, file_content, metadata
            
        except Exception as e:
            return False, b"", {"error": str(e)}

    async def delete_file(self, bucket: str, file_path: str) -> tuple[bool, str]:
        """
        刪除檔案
        
        Args:
            bucket: 儲存桶名稱
            file_path: 檔案路徑
            
        Returns:
            (success, message)
        """
        try:
            self.client.remove_object(bucket, file_path)
            return True, "檔案刪除成功"
            
        except Exception as e:
            return False, f"檔案刪除失敗: {str(e)}"

    async def file_exists(self, bucket: str, file_path: str) -> bool:
        """檢查檔案是否存在"""
        try:
            self.client.stat_object(bucket, file_path)
            return True
        except Exception:
            return False

    async def get_file_info(self, bucket: str, file_path: str) -> Optional[dict]:
        """獲取檔案資訊"""
        try:
            stat = self.client.stat_object(bucket, file_path)
            return {
                "file_path": file_path,
                "bucket": bucket,
                "file_size": stat.size,
                "last_modified": stat.last_modified,
                "etag": stat.etag,
                "metadata": stat.metadata,
                "content_type": stat.content_type,
            }
        except Exception:
            return None


# 全域實例
minio_service = MinIOService()