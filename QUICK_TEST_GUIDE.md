# 🧪 Ticket API 測試實作指南

## 快速開始 (5 分鐘)

### 1. 查看測試項目
```bash
# 列出所有測試
pytest tests/ --collect-only -q
```

### 2. 運行冒煙測試
```bash
# 運行第一個集成測試驗證配置
pytest tests/integration/test_tickets.py::TestTicketIntegration::test_create_and_retrieve_ticket -v
```

### 3. 運行完整測試套件
```bash
# 使用 PowerShell 腳本
./run_tests.ps1 all

# 或直接使用 pytest
pytest tests/ -v --tb=short
```

---

## 📁 測試文件結構

```
tests/
├── conftest.py                          # 全局配置和夾具
├── unit/
│   ├── services/
│   │   └── test_ticket_service.py       # 服務層測試
│   └── routers/
│       └── test_ticket_router.py        # 路由層測試
└── integration/
    └── test_tickets.py                  # 集成測試 (60+ 個測試)
```

---

## 🎯 主要測試功能

### ✅ 已實作的測試
- **建立工單**: POST `/api/v1/tickets/` ✅
- **查詢列表**: GET `/api/v1/tickets/` (分頁、篩選、排序) ✅
- **查詢工單**: GET `/api/v1/tickets/{id}` ✅
- **按工單號查詢**: GET `/api/v1/tickets/by-ticket-no/{no}` ✅
- **全量更新**: PATCH `/api/v1/tickets/{id}` ✅
- **更新標題**: PATCH `/api/v1/tickets/{id}/title` ✅
- **更新描述**: PATCH `/api/v1/tickets/{id}/description` ✅
- **更新指派**: PATCH `/api/v1/tickets/{id}/assignee` ✅
- **更新標籤**: PATCH `/api/v1/tickets/{id}/labels` ✅

### ⏳ 未實作的測試
- **更新狀態**: PATCH `/api/v1/tickets/{id}/status` (端點未實作)

### 📊 測試統計
- **總測試數**: 60+
- **端點覆蓋**: 9/10 (90%)
- **功能覆蓋**: ~85%
- **估計運行時間**: 10-15 秒

---

## 🚀 執行指令參考

### 使用 PowerShell 腳本 (推薦)

```powershell
# 運行所有測試
./run_tests.ps1 all

# 運行單元測試
./run_tests.ps1 unit

# 運行集成測試
./run_tests.ps1 integration

# 運行帶覆蓋率的測試
./run_tests.ps1 coverage

# 運行路由層測試
./run_tests.ps1 router

# 運行服務層測試
./run_tests.ps1 service

# 運行冒煙測試
./run_tests.ps1 smoke

# 快速測試 (不含集成測試)
./run_tests.ps1 quick
```

### 直接使用 pytest

```bash
# 所有測試
pytest tests/ -v

# 特定檔案
pytest tests/integration/test_tickets.py -v

# 特定類別
pytest tests/integration/test_tickets.py::TestTicketIntegration -v

# 特定測試方法
pytest tests/integration/test_tickets.py::TestTicketIntegration::test_create_and_retrieve_ticket -v

# 帶覆蓋率
pytest tests/ --cov=app --cov-report=html --cov-report=term-missing

# 詳細輸出
pytest tests/ -vv --tb=long

# 平行執行 (需要 pytest-xdist)
pytest tests/ -n auto
```

---

## 📖 文檔

| 文件 | 內容 |
|-----|------|
| **TEST_SUMMARY.md** | 實作摘要報告 |
| **TESTING.md** | 詳細測試文檔 |
| **TEST_IMPLEMENTATION.md** | 實作細節 |
| **run_tests.ps1** | 測試執行腳本 |

---

## 🔍 測試示例

### 範例 1: 建立並查詢工單
```python
# tests/integration/test_tickets.py
def test_create_and_retrieve_ticket(self, client, auth_headers, test_db_session):
    # 建立工單
    response = client.post("/api/v1/tickets/",
        json={"title": "Test", "priority": "high"},
        headers=auth_headers(user_id=1)
    )
    assert response.status_code == 201
    ticket_id = response.json()["id"]

    # 查詢工單
    response = client.get(f"/api/v1/tickets/{ticket_id}",
        headers=auth_headers(user_id=1)
    )
    assert response.status_code == 200
```

### 範例 2: 權限測試
```python
# 非建立者無法編輯
def test_non_creator_cannot_update(self, client, auth_headers, sample_ticket):
    response = client.patch(
        f"/api/v1/tickets/{sample_ticket.id}/title",
        json={"title": "Updated"},
        headers=auth_headers(user_id=999)  # 不同用戶
    )
    assert response.status_code == 403
```

### 範例 3: 驗證測試
```python
# 標題長度限制
def test_title_exceeds_max_length(self, client, auth_headers):
    response = client.post("/api/v1/tickets/",
        json={"title": "x" * 201},  # 超過 max_length=200
        headers=auth_headers()
    )
    assert response.status_code == 422
```

---

## 🛠️ 故障排除

### 問題 1: 401 Unauthorized
**症狀**: 所有 API 調用返回 401
**解決**:
- 檢查 auth_headers fixture 是否正確生成 JWT token
- 確保 token 包含 `sub` claim (user_id)

### 問題 2: 422 Validation Error
**症狀**: 建立工單時返回 422
**解決**:
- 檢查 priority 是否為小寫 (low, medium, high, urgent)
- 檢查 visibility 是否為小寫 (internal, restricted)
- 檢查必填欄位是否提供 (title)

### 問題 3: conftest 找不到
**症狀**: ImportError: cannot import name...
**解決**:
- 確保在項目根目錄執行 pytest
- 檢查 conftest.py 是否在 tests/ 目錄

---

## 📊 測試覆蓋報告

運行以下指令生成 HTML 覆蓋率報告:
```bash
pytest tests/ --cov=app --cov-report=html
# 在 htmlcov/index.html 查看報告
```

---

## 🎓 進階使用

### 只運行失敗的測試
```bash
pytest tests/ --lf
```

### 在首個失敗時停止
```bash
pytest tests/ -x
```

### 按標記執行測試
```bash
pytest tests/ -m integration  # 只執行集成測試
pytest tests/ -m unit       # 只執行單元測試
```

### 顯示打印輸出
```bash
pytest tests/ -s
```

---

## ✅ 測試清單

使用以下清單驗證所有主要場景:

- [ ] 建立工單 (201)
- [ ] 查詢工單列表 (200)
- [ ] 查詢單一工單 (200)
- [ ] 不存在的工單 (404)
- [ ] 更新工單標題 (200)
- [ ] 非建立者無法更新 (403)
- [ ] 無效優先級 (422)
- [ ] 空標題 (422)
- [ ] 標題過長 (422)
- [ ] 帶分類和標籤的工單 (201)
- [ ] 分頁查詢 (200)
- [ ] 按工單號查詢 (200)

---

## 📞 常見問題

**Q: 如何新增新的測試?**
A: 在 `tests/integration/test_tickets.py` 中新增測試方法，使用相同的 pattern

**Q: 如何運行單一測試?**
A: `pytest tests/integration/test_tickets.py::TestTicketIntegration::test_name -v`

**Q: 測試數據從哪裡來?**
A: 使用 conftest.py 中的 fixtures (sample_ticket, sample_categories 等)

**Q: 資料庫如何隔離?**
A: 每個測試集合使用獨立的 in-memory SQLite

---

**最後更新**: 2025-10-24 | **狀態**: ✅ 生產就緒
