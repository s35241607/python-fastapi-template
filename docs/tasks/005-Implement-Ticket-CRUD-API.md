# 005-Implement-Ticket-CRUD-API

## 描述
實作工單的基本 CRUD API，包括建立、查詢、更新、刪除。

## 依賴
- 004-Extend-BaseRepository

## 估計時間
2-3 天

## 交付物
- app/routers/tickets.py
- app/schemas/ticket.py
- API 端點：GET/POST/PUT/DELETE /tickets

## 詳細任務
1. 定義 Pydantic schemas (TicketCreate, TicketUpdate)
2. 實作 TicketRepository 繼承 BaseRepository
3. 建立 router 端點
4. 支援工單編號自動生成 (ticket_no)

## 驗收標準
### 功能驗收
- [ ] CRUD 操作正常
- [ ] ticket_no 唯一且自動生成

### Code Review 標準
- [ ] API 遵循 RESTful 原則
- [ ] Schemas 驗證完整

### 測試標準
- [ ] API 測試通過

### 效能標準
- [ ] 回應時間 < 500ms

### 安全標準
- [ ] 輸入驗證防止注入
