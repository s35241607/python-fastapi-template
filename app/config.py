from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "FastAPI Template"
    app_version: str = "1.0.0"
    debug: bool = False
    database_url: str | None = None
    db_schema: str = "ticket"
    secret_key: str = "your-secret-key-here"

    # MinIO 配置 - 適用於 production 環境
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = ""
    minio_secret_key: str = ""
    minio_secure: bool = True  # production 環境應使用 HTTPS
    minio_region: str = ""  # 本地 MinIO 不需要 region
    
    # 儲存桶配置
    minio_bucket_attachments: str = "ticket-attachments"
    minio_bucket_images: str = "ticket-images"
    
    # 檔案大小限制 (bytes)
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    max_image_size: int = 10 * 1024 * 1024  # 10MB
    
    # 允許的檔案類型
    allowed_file_types: list[str] = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/plain",
        "text/csv",
        "application/zip",
        "application/x-rar-compressed",
        "application/json",
    ]
    
    allowed_image_types: list[str] = [
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "image/svg+xml",
    ]
    
    # 檔案 URL 有效期限 (秒)
    file_url_expiry: int = 3600  # 1 小時
    
    # CDN 配置 (production 環境使用)
    cdn_domain: str | None = None  # 例如: "https://cdn.example.com"

    model_config = ConfigDict(env_file=".env")


settings = Settings()
