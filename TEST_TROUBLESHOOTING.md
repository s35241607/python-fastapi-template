# 🧪 測試問題診斷和解決方案

## 當前狀態
- **總測試**:  129 個
- **通過**: 83 個 ✅
- **失敗**: 46 個 ❌

---

## 核心問題

你的 Ticket API 使用了 **schema 功能**（所有表都在 `ticket` schema），但測試框架試圖使用 **SQLite**，而 **SQLite 不支持 schema**。

### 問題堆疊
1. ❌ conftest.py 中的 async fixtures 沒有使用 `@pytest_asyncio.fixture` 裝飾器
   - 已修復 ✅

2. ❌ 缺少 `aiosqlite` 套件
   - 已修復 ✅

3. ❌ SQLite 不支持 schema（`ticket.*` 表前綴）
   - **尚未完全修復** ⏳

---

## 推薦解決方案

### 方案 A：使用 PostgreSQL（推薦 ⭐⭐⭐）

最簡單和完整的解決方案。修改 `tests/conftest.py`:

```python
# 改為使用 PostgreSQL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost/test_tickets"

# 或使用 Docker Compose（最簡單）
docker-compose up postgres  # 在專案根目錄
```

**優點**:
- ✅ 完全支持 schema
- ✅ 無需修改模型或測試
- ✅ 更接近生產環境
- ✅ 測試結果可靠

### 方案 B：暫時禁用測試的 schema（快速修復）

修改所有模型的 `__table_args__` 以支持測試環境:

```python
# 在每個模型中
@property
def __table_args__(cls):
    if os.getenv("PYTEST_RUNNING"):
        return {}  # SQLite 測試時無 schema
    return {"schema": settings.db_schema}
```

**缺點**:
- ❌ 複雜性高
- ❌ 模型代碼污染
- ❌ 不推薦

### 方案 C：暫時禁用 integration 測試，只運行 unit 測試

```bash
pytest tests/unit/ -v  # 暫時跳過集成測試
```

**缺點**:
- ❌ 集成測試無法運行
- ⏳ 臨時方案

---

## 立即行動計劃

### 短期（1-2 小時）
1. **安裝 PostgreSQL** 或使用 Docker
2. **更新 conftest.py** 使用 PostgreSQL
3. **運行所有測試** 應該會全部通過

### 長期
1. 將 PostgreSQL 設置添加到 `docker-compose.yml`
2. 在 CI/CD 管道中使用 PostgreSQL
3. 文檔化測試設置步驟

---

## 快速修復步驟（使用 Docker Postgres）

如果你已安裝 Docker:

```bash
# 1. 建立 docker-compose.yml（如果尚未存在）
docker-compose up -d postgres

# 2. 等待 Postgres 啟動（約 5 秒）
sleep 5

# 3. 修改 conftest.py:
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/test_tickets"

# 4. 運行測試
uv run pytest tests/ -v
```

---

## 當前測試摘要

```
✅ 83 個測試通過（主要是單元測試）
❌ 46 個測試失敗（主要是集成測試 - SQLite schema 問題）
```

### 已通過的測試
- ✅ 所有 repository 單元測試
- ✅ 所有 service 單元測試
- ✅ 所有 router 單元測試（使用 mocked service）
- ✅ 基本的 fixtures 設置

### 失敗的測試
- ❌ 所有集成測試（需要真實資料庫）
  - 因為 SQLite 不能建立帶 schema 前綴的表

---

##建議

**立即行動**: 使用 PostgreSQL 替代 SQLite
- 只需修改 `conftest.py` 中的一行 URL
- 所有 129 個測試應該會通過 ✅

需要幫助設置 PostgreSQL 嗎？告訴我！

---

**最後更新**: 2025-10-24
