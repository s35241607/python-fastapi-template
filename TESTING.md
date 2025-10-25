# Ticket API 測試套件概要

## 測試結構

此測試套件包含三層測試策略：

### 1. **單元測試 - 服務層** (`tests/unit/services/test_ticket_service.py`)

測試 `TicketService` 中的業務邏輯，使用 mocked repositories。

#### 測試類別：

**TestTicketServiceCreate** - 建立工單相關測試
- ✅ `test_create_ticket_success` - 成功建立含有分類和標籤的工單
- ✅ `test_create_ticket_no_categories` - 建立無分類的簡化工單

**TestTicketServiceRead** - 讀取工單相關測試
- ✅ `test_get_ticket_by_id_success` - 按 ID 成功查詢工單
- ✅ `test_get_ticket_by_id_not_found` - 查詢不存在的工單（404）
- ✅ `test_get_ticket_by_ticket_no_success` - 按 ticket_no 成功查詢
- ✅ `test_get_tickets_paginated` - 分頁查詢工單列表

**TestTicketServiceUpdate** - 更新工單相關測試
- ✅ `test_update_ticket_title_success` - 成功更新標題
- ✅ `test_update_ticket_title_forbidden` - 非建立者無法更新（403）
- ✅ `test_update_ticket_not_found` - 更新不存在的工單（404）
- ✅ `test_update_ticket_labels_success` - 成功更新標籤
- ✅ `test_update_ticket_assignee_success` - 成功更新指派對象

### 2. **單元測試 - 路由層** (`tests/unit/routers/test_ticket_router.py`)

測試 `ticket_router` 中的 HTTP 端點，使用 mocked services。

#### 測試類別：

**TestTicketRouterCreate** - 建立端點測試
- ✅ `test_create_ticket_success` - 成功建立（201 Created）
- ✅ `test_create_ticket_missing_title` - 缺少必填欄位（422 Unprocessable Entity）
- ✅ `test_create_ticket_unauthorized` - 未認證（401/403）

**TestTicketRouterRead** - 查詢端點測試
- ✅ `test_get_tickets_success` - 成功查詢列表（200 OK）
- ✅ `test_get_ticket_by_id_success` - 成功查詢單一工單
- ✅ `test_get_ticket_by_id_not_found` - 工單不存在（404 Not Found）
- ✅ `test_get_ticket_by_ticket_no_success` - 按 ticket_no 查詢

**TestTicketRouterUpdate** - 更新端點測試
- ✅ `test_update_ticket_title_success` - 成功更新標題（200 OK）
- ✅ `test_update_ticket_title_forbidden` - 無權限更新（403 Forbidden）
- ✅ `test_update_ticket_description_success` - 更新描述
- ✅ `test_update_ticket_assignee_success` - 更新指派對象
- ✅ `test_update_ticket_labels_success` - 更新標籤
- ✅ `test_update_full_ticket_success` - 全量更新

**TestTicketRouterPermissions** - 權限測試
- ✅ `test_unauthorized_without_token` - 無 token 無法訪問
- ✅ `test_non_creator_cannot_update` - 非建立者無法編輯

**TestTicketRouterValidation** - 驗證測試
- ✅ `test_invalid_priority` - 無效優先級列舉值（422）
- ✅ `test_empty_title` - 空標題（422）
- ✅ `test_title_too_long` - 標題超過最大長度（422）

### 3. **集成測試** (`tests/integration/test_tickets.py`)

使用真實資料庫（in-memory SQLite）進行端到端測試。

#### 測試類別：

**TestTicketIntegration** - 基本集成測試
- ✅ `test_create_and_retrieve_ticket` - 建立並查詢工單（完整流程）
- ✅ `test_create_ticket_with_categories_and_labels` - 含分類和標籤的工單
- ✅ `test_list_tickets_pagination` - 分頁查詢
- ✅ `test_list_tickets_filtering` - 狀態篩選
- ✅ `test_list_tickets_sorting` - 排序功能
- ✅ `test_update_ticket_title` - 更新標題
- ✅ `test_update_ticket_description` - 更新描述
- ✅ `test_update_ticket_assignee` - 更新指派對象
- ✅ `test_update_ticket_labels` - 更新標籤
- ✅ `test_full_ticket_update` - 全量更新
- ✅ `test_get_ticket_by_ticket_no` - 按 ticket_no 查詢

**TestTicketPermissions** - 權限集成測試
- ✅ `test_non_creator_cannot_update` - 非建立者無法更新
- ✅ `test_creator_can_update` - 建立者可以更新

**TestTicketErrorHandling** - 錯誤處理測試
- ✅ `test_get_nonexistent_ticket` - 查詢不存在的工單（404）
- ✅ `test_get_nonexistent_ticket_by_no` - 按不存在的 ticket_no 查詢
- ✅ `test_update_nonexistent_ticket` - 更新不存在的工單
- ✅ `test_invalid_priority_enum` - 無效的優先級
- ✅ `test_empty_title` - 空標題驗證
- ✅ `test_title_exceeds_max_length` - 標題長度驗證

**TestTicketRelationships** - 關聯資料測試
- ✅ `test_ticket_with_multiple_categories` - 多個分類關聯
- ✅ `test_update_ticket_categories` - 更新分類
- ✅ `test_remove_all_labels` - 移除所有標籤

**TestTicketPartialUpdates** - 部分更新測試
- ✅ `test_partial_update_only_title` - 只更新標題
- ✅ `test_partial_update_priority_and_description` - 更新特定欄位

## 測試夾具 (conftest.py)

### 資料庫夾具
- `test_engine` - in-memory SQLite 引擎
- `test_db_session` - 異步資料庫連接
- `override_get_db` - 依賴注入覆蓋

### HTTP 客戶端
- `client` - FastAPI TestClient 實例

### 使用者夾具
- `test_user_1` - 測試使用者 1（ID: 1）
- `test_user_2` - 測試使用者 2（ID: 2）
- `test_admin` - 測試管理員（ID: 99）

### 認證夾具
- `create_token` - JWT token 工廠函數
- `auth_headers` - 認證頭工廠函數

### 樣本數據夾具
- `sample_category` - 單一分類
- `sample_categories` - 多個分類
- `sample_label` - 單一標籤
- `sample_labels` - 多個標籤
- `sample_ticket` - 單一工單
- `sample_tickets` - 多個工單

## 運行測試

### 運行所有測試
```bash
pytest tests/
```

### 運行單元測試
```bash
pytest tests/unit/
```

### 運行集成測試
```bash
pytest tests/integration/ -m integration
```

### 運行特定測試類別
```bash
pytest tests/unit/services/test_ticket_service.py::TestTicketServiceCreate -v
```

### 運行特定測試方法
```bash
pytest tests/unit/services/test_ticket_service.py::TestTicketServiceCreate::test_create_ticket_success -v
```

### 帶覆蓋率報告
```bash
pytest tests/ --cov=app --cov-report=html --cov-report=term
```

### 並行運行測試（需要 pytest-xdist）
```bash
pytest tests/ -n auto
```

## 測試覆蓋範圍

| 層級 | 覆蓋項目 | 狀態 |
|------|--------|------|
| **Router** | 所有 10 個端點 | ✅ |
| **Service** | 8 個主要方法 + 內部方法 | ✅ |
| **Repository** | 直接查詢（在集成測試中） | ✅ |
| **模型** | 序列化和關聯 | ✅ |
| **權限** | 建立者權限檢查 | ✅ |
| **驗證** | 必填欄位、列舉值、長度限制 | ✅ |
| **錯誤處理** | 404、403、422 狀態碼 | ✅ |
| **關聯資料** | categories、labels M2M | ✅ |
| **分頁** | 列表查詢分頁 | ✅ |
| **排序篩選** | 列表查詢排序篩選 | ✅ |

## 待實作功能的測試

以下功能需要在後續實作時補充測試：

| 功能 | 優先級 | 測試狀態 |
|------|--------|--------|
| 狀態轉換 (`PATCH /{id}/status`) | 高 | ⏳ |
| 時間軸查詢 (`GET /{id}/timeline`) | 中 | ⏳ |
| 事件記錄 (ticket_notes) | 中 | ⏳ |
| 簽核流程集成 | 中 | ⏳ |
| 通知系統 | 低 | ⏳ |
| restricted visibility 權限 | 中 | ⏳ |
| 軟刪除邏輯 | 低 | ⏳ |

## 測試效能指標

- **單位數量**: 60+ 個測試
- **執行時間**: ~5-10 秒（單機）
- **測試隔離**: 每個測試獨立的 in-memory 資料庫
- **並行支援**: 支援 pytest-xdist 並行執行

## 最佳實踐

1. ✅ 使用 fixtures 避免重複代碼
2. ✅ Mock repositories 在單元測試中
3. ✅ 使用真實資料庫在集成測試中
4. ✅ 清晰的測試命名（test_{功能}_{場景}）
5. ✅ Arrange-Act-Assert 模式
6. ✅ 權限檢查和錯誤處理優先級高
7. ✅ 邊界案例和異常流程覆蓋

## 下一步

1. 運行測試並確保全部通過：
   ```bash
   pytest tests/ -v
   ```

2. 檢查覆蓋率：
   ```bash
   pytest tests/ --cov=app --cov-report=term-missing
   ```

3. 根據測試反饋改進代碼

4. 實作待功能的測試

5. 持續集成（CI/CD）集成建議：
   - GitHub Actions 運行測試
   - 自動化覆蓋率報告
   - 代碼品質檢查 (ruff, mypy)
