# 014-Implement-Static-Permissions

## 描述
實作靜態權限檢查，基於 visibility 和 ticket_view_permissions。

## 依賴
- 005-Implement-Ticket-CRUD-API

## 估計時間
2 天

## 交付物
- PermissionService
- GET /tickets 過濾邏輯

## 詳細任務
1. 實作可見性檢查 (internal vs restricted)
2. 支援用戶/角色權限表查詢
3. 整合到所有工單 API

## 驗收標準
### 功能驗收
- [ ] 可見性過濾正確
- [ ] 權限檢查生效

### Code Review 標準
- [ ] 權限邏輯清晰，並通過 ruff 檢查

### 測試標準
- [ ] 權限測試通過

### 效能標準
- [ ] 檢查 < 50ms

### 安全標準
- [ ] 防止未授權訪問
