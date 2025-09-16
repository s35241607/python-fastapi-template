# 007-Implement-Unified-Timeline

## 描述
實作統一事件時間軸，記錄所有工單相關事件和用戶留言。

## 依賴
- 006-Implement-Ticket-Lifecycle-Logic

## 估計時間
2 天

## 交付物
- GET/POST /tickets/{id}/notes 端點
- ticket_notes 記錄邏輯

## 詳細任務
1. 實作 NoteRepository 和 schemas
2. 區分系統事件和用戶留言
3. 支援事件類型和 JSONB 詳細資訊

## 驗收標準
### 功能驗收
- [ ] 用戶留言和系統事件正確儲存
- [ ] 時間軸查詢正確排序

### Code Review 標準
- [ ] 程式碼模組化，並通過 ruff 檢查
- [ ] 事件類型枚舉正確使用

### 測試標準
- [ ] 留言 CRUD 測試通過

### 效能標準
- [ ] 查詢時間軸 < 100ms

### 安全標準
- [ ] 留言內容過濾防止 XSS
