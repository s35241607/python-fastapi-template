# FastAPI Template

一個快速的 FastAPI 專案模板，包含完整的專案結構和環境變數設定。

## 專案結構

```
python-fastapi-template/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI 應用程式
│   ├── config.py        # 設定和環境變數
│   ├── routers/
│   │   ├── __init__.py
│   │   └── items.py     # 範例路由
│   ├── models/
│   │   ├── __init__.py
│   │   └── item.py      # 資料模型
│   └── schemas/
│       ├── __init__.py
│       └── item.py      # Pydantic 模式
├── tests/
│   ├── __init__.py
│   └── test_main.py     # 測試文件
├── .env                 # 環境變數
├── main.py              # 應用程式入口點
├── pyproject.toml       # 專案依賴
├── uv.lock              # uv 鎖定文件
└── README.md
```

## 環境變數

編輯 `.env` 文件來設定環境變數：

- `APP_NAME`: 應用程式名稱
- `APP_VERSION`: 應用程式版本
- `DEBUG`: 除錯模式
- `DATABASE_URL`: 資料庫 URL
- `SECRET_KEY`: 秘密金鑰

## 運行應用程式

```bash
# 安裝依賴
uv sync

# 運行應用程式
python main.py
```

應用程式將在 http://localhost:8000 運行。

## API 端點

- `GET /`: 歡迎訊息
- `GET /api/v1/items/`: 獲取所有項目
- `GET /api/v1/items/{item_id}`: 獲取特定項目
- `POST /api/v1/items/`: 建立新項目
- `PUT /api/v1/items/{item_id}`: 更新項目
- `DELETE /api/v1/items/{item_id}`: 刪除項目

## 測試

```bash
# 運行測試
pytest
```
