# 002-Implement-SQLAlchemy-Models

## 描述
基於 ticket_system_schema.sql 實作所有 SQLAlchemy 模型，包括表定義、關聯、ENUM 類型。確保模型支援軟刪除和 JSONB 自訂欄位。

## 依賴
- 001-Setup-Project-Structure

## 估計時間
3-4 天

## 交付物
- app/models/ 下的所有模型檔案 (e.g., ticket.py, user.py 等)
- 模型關聯正確設定

## 詳細任務
1. 定義 ENUM 類型 (ticket_status, priority 等)
2. 實作核心模型：Ticket, TicketTemplate, ApprovalProcess 等
3. 設定外鍵和多對多關聯 (e.g., ticket_categories)
4. 支援 JSONB 欄位 (custom_fields_data, custom_fields_schema)
5. 添加軟刪除欄位 (deleted_at, deleted_by)

## 驗收標準
### 功能驗收
- [ ] 所有模型可正確匯入和實例化
- [ ] 關聯正確 (e.g., Ticket.categories 工作)
- [ ] JSONB 欄位支援讀寫
- [ ] 軟刪除邏輯生效

### Code Review 標準
- [ ] 模型命名符合 SQLAlchemy 慣例，並通過 ruff 檢查
- [ ] 欄位類型正確 (e.g., BigInteger for ID)
- [ ] 無循環依賴
- [ ] 註釋完整 (e.g., 欄位說明)

### 測試標準
- [ ] 模型單元測試通過 (建立/查詢)
- [ ] 關聯測試通過

### 效能標準
- [ ] 查詢無 N+1 問題
- [ ] 索引正確設定

### 安全標準
- [ ] 無 SQL 注入風險 (使用 ORM)
