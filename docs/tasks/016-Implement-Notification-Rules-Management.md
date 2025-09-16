# 016-Implement-Notification-Rules-Management

## 描述
實作通知規則的 CRUD。

## 依賴
- 004-Extend-BaseRepository

## 估計時間
1-2 天

## 交付物
- GET/POST /notification-rules 端點

## 詳細任務
1. 支援基於範本或工單的規則
2. 管理通知用戶/角色

## 驗收標準
### 功能驗收
- [ ] 規則 CRUD 正常
- [ ] 用戶/角色關聯正確

### Code Review 標準
- [ ] 規則邏輯清晰，並通過 ruff 檢查

### 測試標準
- [ ] 規則測試通過

### 效能標準
- [ ] 查詢 < 100ms

### 安全標準
- [ ] 驗證規則權限
