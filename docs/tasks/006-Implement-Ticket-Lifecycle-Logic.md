# 006-Implement-Ticket-Lifecycle-Logic

## 描述
實作工單狀態機邏輯，包括狀態轉換規則和業務邏輯。

## 依賴
- 005-Implement-Ticket-CRUD-API

## 估計時間
3-4 天

## 交付物
- TicketService 類
- PATCH /tickets/{id}/status 端點
- 狀態轉換驗證

## 詳細任務
1. 實作狀態機：draft → waiting_approval → open → in_progress → resolved → closed
2. 添加業務規則：角色檢查、自動指派等
3. 整合事件記錄到 ticket_notes

## 驗收標準
### 功能驗收
- [ ] 狀態轉換正確遵循 SPEC 規則
- [ ] 業務邏輯 (e.g., 角色檢查) 生效
- [ ] 事件記錄到 ticket_notes

### Code Review 標準
- [ ] 狀態機邏輯清晰，並通過 ruff 檢查
- [ ] 錯誤處理完善 (e.g., 無效轉換拋異常)
- [ ] 無業務邏輯洩露到控制器

### 測試標準
- [ ] 狀態轉換測試通過
- [ ] 邊界情況測試 (e.g., 無效狀態)

### 效能標準
- [ ] 狀態更新 < 200ms

### 安全標準
- [ ] 權限檢查防止未授權狀態變更
