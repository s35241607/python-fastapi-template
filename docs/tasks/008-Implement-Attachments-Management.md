# 008-Implement-Attachments-Management

## 描述
實作附件上傳、下載和管理，包括工單附件和留言附件。

## 依賴
- 005-Implement-Ticket-CRUD-API

## 估計時間
2-3 天

## 交付物
- GET/POST /tickets/{id}/attachments 端點
- 檔案儲存服務

## 詳細任務
1. 實作檔案上傳邏輯 (支援 ticket_attachments 和 ticket_note_attachments)
2. 添加檔案類型和大小驗證
3. 支援檔案下載和刪除

## 驗收標準
### 功能驗收
- [ ] 檔案上傳/下載正常
- [ ] 驗證生效 (e.g., 大小限制)

### Code Review 標準
- [ ] 檔案處理安全，並通過 ruff 檢查

### 測試標準
- [ ] 檔案操作測試通過

### 效能標準
- [ ] 上傳/下載 < 2 秒

### 安全標準
- [ ] 防止檔案上傳漏洞
