# FastAPI Ticket System

一個完整的 FastAPI 專案，使用 router > service > repository 架構，支援 async PostgreSQL 資料庫操作。

## 專案結構

```
python-fastapi-template/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 應用程式
│   ├── config.py            # 設定和環境變數
│   ├── database.py          # 資料庫連線
│   ├── routers/
│   │   ├── __init__.py
│   │   └── items.py         # Ticket 路由 (改名為 tickets)
│   ├── models/
│   │   ├── __init__.py      # 匯入所有模型
│   │   ├── base.py          # SQLAlchemy 基礎模型
│   │   ├── user.py          # User 模型
│   │   ├── ticket.py        # Ticket 模型
│   │   └── comment.py       # Comment 模型
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── item.py          # Pydantic 模式
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py          # 基礎 repository
│   │   ├── user_repository.py
│   │   ├── ticket_repository.py
│   │   └── comment_repository.py
│   └── services/
│       ├── __init__.py
│       └── ticket_service.py # 業務邏輯服務
├── tests/
│   ├── __init__.py
│   └── test_main.py         # 測試文件
├── specs/
│   └── 001-fastapi-api-ticket/
├── .env                     # 環境變數
├── .env.example             # 環境變數範例
├── init_db.py               # 資料庫初始化腳本
├── main.py                  # 應用程式入口點
├── pyproject.toml           # 專案依賴
├── uv.lock                  # uv 鎖定文件
└── README.md
```

## 架構說明

### Router > Service > Repository 模式

1. **Router 層**: 處理 HTTP 請求，驗證輸入，調用 Service
2. **Service 層**: 包含業務邏輯，協調多個 Repository 操作
3. **Repository 層**: 處理資料存取，與資料庫互動

### Async PostgreSQL

- 使用 SQLAlchemy 2.0 async 功能
- asyncpg 作為資料庫驅動
- 支援非同步資料庫操作

## 環境變數

複製 `.env.example` 到 `.env` 並設定：

```bash
DATABASE_URL=postgresql+asyncpg://username:password@localhost/ticket_db
SECRET_KEY=your-secret-key-here
DEBUG=True
```

## 資料庫設定

1. 建立 PostgreSQL 資料庫
2. 更新 `.env` 中的 `DATABASE_URL`
3. 運行初始化腳本：

```bash
python init_db.py
```

## 運行應用程式

```bash
# 安裝依賴
uv sync

# 初始化資料庫
python init_db.py

# 運行應用程式
python main.py
```

應用程式將在 http://localhost:8000 運行。

## API 端點

### Tickets

- `POST /api/v1/tickets/`: 建立 ticket 並添加初始 comment
- `GET /api/v1/tickets/`: 獲取所有 tickets (包含 user 和 comments)
- `GET /api/v1/tickets/{ticket_id}`: 獲取特定 ticket 詳細資訊
- `PUT /api/v1/tickets/{ticket_id}/status`: 更新 ticket 狀態
- `DELETE /api/v1/tickets/{ticket_id}`: 刪除 ticket 及其所有 comments
- `POST /api/v1/tickets/{ticket_id}/comments/`: 為 ticket 添加 comment

## 複雜 CRUD 案例

### 建立 Ticket 與初始 Comment
```json
POST /api/v1/tickets/
{
  "ticket": {
    "title": "系統錯誤",
    "description": "應用程式崩潰",
    "user_id": 1
  },
  "initial_comment": {
    "content": "發現系統錯誤，需要修復",
    "user_id": 1
  }
}
```

### 更新 Ticket 狀態 (自動添加系統 Comment)
```json
PUT /api/v1/tickets/1/status?user_id=1
"in_progress"
```

### 刪除 Ticket (級聯刪除 Comments)
```json
DELETE /api/v1/tickets/1?user_id=1
```

## 測試

```bash
# 運行測試
pytest
```

## 資料庫模型

- **User**: 用戶資訊
- **Ticket**: 工單，包含狀態追蹤
- **Comment**: 工單評論，支援多用戶

所有操作都是非同步的，並支援複雜的關聯查詢。
