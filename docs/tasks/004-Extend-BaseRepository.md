# 004-Extend-BaseRepository

## 描述
擴充 BaseRepository 以支援軟刪除過濾、查詢方法和事務處理。

## 依賴
- 002-Implement-SQLAlchemy-Models

## 估計時間
1 天

## 交付物
- 更新後的 app/repositories/base.py
- 新增方法：get_all_active, soft_delete 等

## 詳細任務
1. 修改 get_all 和 get_by_id 以過濾 deleted_at IS NULL
2. 添加 soft_delete 方法 (更新 deleted_at)
3. 添加查詢方法：find_by_field, paginate
4. 支援事務上下文

## 驗收標準
### 功能驗收
- [ ] 軟刪除過濾生效
- [ ] 新方法工作正確

### Code Review 標準
- [ ] 程式碼 DRY (Don't Repeat Yourself)
- [ ] 錯誤處理完善

### 測試標準
- [ ] Repository 測試通過

### 效能標準
- [ ] 查詢效能良好

### 安全標準
- [ ] 無 SQL 注入
