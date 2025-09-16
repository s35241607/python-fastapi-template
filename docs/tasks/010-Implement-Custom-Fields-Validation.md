# 010-Implement-Custom-Fields-Validation

## 描述
實作自訂欄位的驗證和處理邏輯。

## 依賴
- 005-Implement-Ticket-CRUD-API

## 估計時間
2 天

## 交付物
- CustomFieldsService 類
- JSONB 驗證邏輯

## 詳細任務
1. 驗證 custom_fields_data 符合 custom_fields_schema
2. 支援動態欄位類型 (text, number, date 等)
3. 整合到工單建立/更新流程

## 驗收標準
### 功能驗收
- [ ] 驗證正確拒絕無效資料
- [ ] 動態欄位支援

### Code Review 標準
- [ ] 驗證邏輯模組化，並通過 ruff 檢查

### 測試標準
- [ ] 驗證測試通過

### 效能標準
- [ ] 驗證 < 50ms

### 安全標準
- [ ] 防止惡意輸入
