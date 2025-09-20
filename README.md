# FastAPI Ticket System

一個以 FastAPI 建構的企業級工單系統樣板，採用 router > service > repository 架構，支援 SQLAlchemy 2.0 非同步 ORM。資料庫預設為 SQLite（便於本機開發），可透過 `DATABASE_URL` 切換到 PostgreSQL（搭配 asyncpg）。

## 目前狀態

✅ 架構與基礎元件已就緒：
- FastAPI 應用初始化、CORS 設定
- 非同步資料庫與 DI session（`app.database.get_db`）
- Alembic 已設定僅針對 `ticket` schema 的遷移
- 路由：`/` 公開路由、`/api/v1/categories` 類別 CRUD（JWT Bearer 依賴，但開發模式不驗證簽章）

## 專案結構（關鍵檔案）

```
app/
  main.py           # FastAPI 應用、CORS、例外處理、路由掛載
  config.py         # 設定（env：app_name、app_version、debug、database_url、db_schema）
  database.py       # Async engine/session、get_db DI；預設 SQLite
  auth/dependencies.py  # get_user_id_from_jwt（開發模式不驗簽）
  routers/
    public_router.py    # GET /
    category_router.py  # /api/v1/categories CRUD（依賴 get_user_id_from_jwt）
  services/
    category_service.py # 業務邏輯（使用 Repository）
  repositories/
    base_repository.py  # 泛型 CRUD、軟刪除欄位支援
    category_repository.py
  models/
    base.py, enums.py, ticket.py, category.py, ... # 皆位於 ticket schema
alembic/               # 遷移（已過濾至 ticket schema）
docs/SPEC.md           # 詳細規格與流程
tests/test_main.py     # 範例測試
main.py                # 本機啟動入口（同 uvicorn）
```

## 快速開始

```pwsh
# 安裝相依
uv sync

# 初始化資料庫（依 app.database 設定；預設 SQLite 建表）
uv run python init_db.py

# 啟動開發伺服器
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 執行測試
uv run pytest

# 品質工具
uv run ruff check . --fix
uv run ruff format .
uv run mypy .
```

服務將於 http://localhost:8000 提供；Swagger UI 在 http://localhost:8000/docs。

## 環境變數（`.env`）

```env
# 若未提供，預設使用 SQLite：sqlite+aiosqlite:///./test.db
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost/postgres
SECRET_KEY=your-secret-key-here
DEBUG=true
```

> Alembic 的 `alembic.ini` 已預設連線至 PostgreSQL；若使用 Alembic 進行遷移，請確保資料庫可連線並與 `app.config.settings.db_schema` 一致（預設 `ticket`）。

## 認證與權限

- 以 Bearer JWT 驗證；在 `app.auth.dependencies.get_user_id_from_jwt` 中為開發模式，未驗證簽章，僅讀取 `sub` 作為使用者 ID。
- 權限與可見性（`internal`/`restricted`）與審計軌跡、簽核流程等完整規格，請參考 `docs/SPEC.md` 與模型定義（`app/models`）。

## 已提供的 API 範例

- `GET /`：健康與歡迎訊息（public）
- `POST /api/v1/categories/`：建立分類（需要 Bearer）
- `GET /api/v1/categories/`：取得所有分類
- `GET /api/v1/categories/{id}`：取得單一分類
- `PUT /api/v1/categories/{id}`：更新分類
- `DELETE /api/v1/categories/{id}`：軟刪除分類
- `DELETE /api/v1/categories/{id}/hard`：硬刪除（若實作）

> Tickets/Approvals/Labels 等完整資源的資料模型與遷移已備妥，路由與服務可依 `category` 範例擴充。

## 架構與慣例

- Router 只處理輸入驗證與委派；Service 負責業務邏輯；Repository 專注資料存取（以 session 注入，見 `BaseRepository`）。
- 共同欄位：`created_by/at`、`updated_by/at`、`deleted_by/at`（軟刪除）。
- Enum 與關聯表集中於 `app/models/enums.py` 與多對多中介表（如 `ticket_categories`, `ticket_labels`）。
- 需要多表變更的業務流程請使用交易（`AsyncSession`）。

## Alembic 遷移

- 已設定只產生/比對 `ticket` schema 的物件（參見 `alembic/env.py` 的 `include_object`）。
- 使用前請確認 `alembic.ini` 的 `sqlalchemy.url` 指向可用的 PostgreSQL。

## 疑難排解

- 若啟動 `uvicorn` 失敗（Exit Code 1），請先檢查 `.env` 中 `DATABASE_URL` 與實際連線設定；或先使用預設 SQLite 並執行 `uv run python init_db.py` 以建表。

---

本樣板旨在快速搭建企業級工單系統後端雛型，詳細業務流程與事件規格請參閱 `docs/SPEC.md`。
