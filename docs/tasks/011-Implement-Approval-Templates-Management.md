# 011-Implement-Approval-Templates-Management

## 描述
實作簽核範本的 CRUD，包括步驟定義。

## 依賴
- 004-Extend-BaseRepository

## 估計時間
2 天

## 交付物
- GET/POST /approval-templates 端點
- ApprovalTemplateRepository

## 詳細任務
1. 實作範本和步驟的 schemas
2. 支援步驟順序和角色/用戶指派
3. 驗證範本完整性

## 驗收標準
### 功能驗收
- [ ] 範本 CRUD 正常
- [ ] 步驟驗證正確

### Code Review 標準
- [ ] 邏輯清晰，並通過 ruff 檢查

### 測試標準
- [ ] 範本測試通過

### 效能標準
- [ ] 查詢 < 100ms

### 安全標準
- [ ] 權限檢查
