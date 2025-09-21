"""
開發環境檢查腳本
在啟動應用程式前檢查所有依賴是否正常
"""

import sys
import importlib
from typing import List, Tuple


def check_dependencies() -> List[Tuple[str, bool, str]]:
    """檢查關鍵依賴"""
    dependencies = [
        ("fastapi", "FastAPI 框架"),
        ("uvicorn", "ASGI 伺服器"),
        ("sqlalchemy", "ORM 框架"),
        ("asyncpg", "PostgreSQL 驅動"),
        ("alembic", "資料庫遷移工具"),
        ("pydantic", "資料驗證"),
        ("minio", "MinIO 客戶端"),
        ("PIL", "圖片處理 (Pillow)"),
        ("aiofiles", "異步檔案操作"),
    ]
    
    results = []
    for module_name, description in dependencies:
        try:
            importlib.import_module(module_name)
            results.append((description, True, "✅ 正常"))
        except ImportError as e:
            results.append((description, False, f"❌ 缺失: {e}"))
    
    return results


def check_optional_dependencies() -> List[Tuple[str, bool, str]]:
    """檢查可選依賴"""
    optional_deps = [
        ("magic", "檔案類型檢測 (可選)"),
        ("redis", "Redis 快取 (可選)"),
        ("celery", "背景任務 (可選)"),
    ]
    
    results = []
    for module_name, description in optional_deps:
        try:
            importlib.import_module(module_name)
            results.append((description, True, "✅ 可用"))
        except ImportError:
            results.append((description, False, "⚠️ 不可用 (可選)"))
    
    return results


def check_environment_variables() -> List[Tuple[str, bool, str]]:
    """檢查重要的環境變數"""
    import os
    from app.config import settings
    
    env_checks = [
        ("DATABASE_URL", settings.database_url, "資料庫連線"),
        ("MINIO_ENDPOINT", settings.minio_endpoint, "MinIO 端點"),
        ("MINIO_ACCESS_KEY", settings.minio_access_key, "MinIO 存取金鑰"),
        ("MINIO_SECRET_KEY", settings.minio_secret_key, "MinIO 秘密金鑰"),
    ]
    
    results = []
    for name, value, description in env_checks:
        if value and value.strip():
            results.append((description, True, f"✅ 已設定"))
        else:
            results.append((description, False, f"❌ 未設定或為空"))
    
    return results


def check_import_paths():
    """檢查重要模組是否能正常導入"""
    modules_to_check = [
        "app.main",
        "app.config",
        "app.database",
        "app.services.minio_service",
        "app.services.attachment_service",
        "app.routers.attachment_router",
    ]
    
    results = []
    for module_name in modules_to_check:
        try:
            importlib.import_module(module_name)
            results.append((module_name, True, "✅ 正常"))
        except Exception as e:
            results.append((module_name, False, f"❌ 錯誤: {e}"))
    
    return results


def main():
    """主檢查函數"""
    print("🔍 開發環境檢查")
    print("=" * 60)
    
    print(f"\n📦 Python 版本: {sys.version}")
    
    # 檢查核心依賴
    print("\n🔧 核心依賴檢查:")
    core_deps = check_dependencies()
    for desc, status, msg in core_deps:
        print(f"  {msg} {desc}")
    
    # 檢查可選依賴
    print("\n🔧 可選依賴檢查:")
    optional_deps = check_optional_dependencies()
    for desc, status, msg in optional_deps:
        print(f"  {msg} {desc}")
    
    # 檢查環境變數
    print("\n⚙️ 環境變數檢查:")
    env_vars = check_environment_variables()
    for desc, status, msg in env_vars:
        print(f"  {msg} {desc}")
    
    # 檢查模組導入
    print("\n📂 模組導入檢查:")
    import_checks = check_import_paths()
    for module, status, msg in import_checks:
        print(f"  {msg} {module}")
    
    # 總結
    print("\n" + "=" * 60)
    
    all_core_ok = all(status for _, status, _ in core_deps)
    all_imports_ok = all(status for _, status, _ in import_checks)
    all_env_ok = all(status for _, status, _ in env_vars)
    
    if all_core_ok and all_imports_ok and all_env_ok:
        print("🎉 所有檢查通過！應用程式應該能正常啟動。")
        return True
    else:
        print("⚠️ 發現問題，請修復後再啟動應用程式。")
        if not all_core_ok:
            print("  - 核心依賴有問題，請執行: uv sync")
        if not all_imports_ok:
            print("  - 模組導入有問題，請檢查程式碼")
        if not all_env_ok:
            print("  - 環境變數有問題，請檢查 .env 檔案")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)