# 001-Setup-Project-Structure

## 描述
設定 FastAPI 專案基本結構，包括 routers, services, repositories, models, schemas 等資料夾和檔案。確保專案符合 SPEC 的架構要求。

## 依賴
- 無

## 估計時間
1-2 天

## 交付物
- 完整的專案資料夾結構
- 基本 FastAPI app.py 和 main.py
- requirements.txt 或 pyproject.toml 更新

## 詳細任務
1. 建立 app/ 子資料夾結構：models/, repositories/, routers/, services/, schemas/, config.py, database.py
2. 初始化 FastAPI 應用，設定 CORS 和中間件
3. 使用 uv 安裝必要依賴：uv add fastapi, sqlalchemy, alembic, uvicorn
4. 設定環境變數和 config.py

## 驗收標準
### 功能驗收
- [ ] 專案結構符合 SPEC 架構要求
- [ ] FastAPI 應用可正常啟動 (uv run uvicorn app.main:app)
- [ ] 所有依賴安裝完成，無衝突
- [ ] 環境變數配置正確 (DATABASE_URL 等)

### Code Review 標準
- [ ] 程式碼遵循 PEP 8 風格，並通過 ruff 檢查
- [ ] 無硬編碼值，使用環境變數
- [ ] 資料夾結構清晰，有 README 說明
- [ ] 無安全漏洞 (e.g., 敏感資訊外洩)

### 測試標準
- [ ] 基本啟動測試通過
- [ ] 依賴安裝測試 (pyproject.toml 驗證)

### 效能標準
- [ ] 應用啟動時間 < 5 秒
- [ ] 記憶體使用合理

### 安全標準
- [ ] 無明文密碼或 API 金鑰
- [ ] CORS 設定安全 (僅允許必要來源)
