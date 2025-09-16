# 012-Implement-Approval-Process-Engine

## 描述
實作簽核流程引擎，包括流程啟動和步驟推進。

## 依賴
- 011-Implement-Approval-Templates-Management

## 估計時間
3-4 天

## 交付物
- ApprovalProcessService
- POST /approval-process-steps/{id}/approve 端點

## 詳細任務
1. 自動建立 approval_processes 和 steps
2. 實作核准/駁回邏輯
3. 狀態推進和通知觸發

## 驗收標準
### 功能驗收
- [ ] 流程自動建立
- [ ] 核准/駁回正確推進

### Code Review 標準
- [ ] 引擎邏輯清晰，並通過 ruff 檢查

### 測試標準
- [ ] 流程測試通過

### 效能標準
- [ ] 推進 < 200ms

### 安全標準
- [ ] 權限檢查
