# 009-Implement-Categories-Labels-Management

## 描述
實作類別和標籤的 CRUD，以及與工單/範本的關聯管理。

## 依賴
- 005-Implement-Ticket-CRUD-API

## 估計時間
2 天

## 交付物
- GET/POST /categories, /labels 端點
- POST/DELETE /tickets/{id}/categories, /labels 端點

## 詳細任務
1. 實作 Category 和 Label repositories
2. 管理多對多關聯 (ticket_categories, ticket_labels)
3. 支援範本關聯 (ticket_template_categories)

## 驗收標準
### 功能驗收
- [ ] CRUD 操作正常
- [ ] 關聯正確

### Code Review 標準
- [ ] 關聯邏輯清晰，並通過 ruff 檢查

### 測試標準
- [ ] 關聯測試通過

### 效能標準
- [ ] 查詢 < 100ms

### 安全標準
- [ ] 無未授權修改
