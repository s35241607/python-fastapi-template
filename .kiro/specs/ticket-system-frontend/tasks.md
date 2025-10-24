# Implementation Plan

- [ ] 1. 專案初始化與基礎配置
  - 使用 Vite 建立 Vue 3 + TypeScript 專案
  - 安裝並配置 Vuetify 3 UI 框架
  - 配置 Pinia 狀態管理
  - 配置 Vue Router
  - 配置 Axios HTTP 客戶端
  - 設定 TypeScript 編譯選項
  - 建立基礎目錄結構
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

- [ ] 2. 建立核心類型定義
  - 建立 `types/ticket.types.ts` 定義工單相關類型 (Ticket, TicketCreate, TicketUpdate, TicketStatus, TicketPriority, TicketVisibility)
  - 建立 `types/template.types.ts` 定義範本相關類型 (TicketTemplate, CustomFieldSchema)
  - 建立 `types/approval.types.ts` 定義簽核相關類型 (ApprovalProcess, ApprovalProcessStep)
  - 建立 `types/category.types.ts` 和 `types/label.types.ts` 定義分類和標籤類型
  - 建立 `types/attachment.types.ts` 定義附件類型
  - 建立 `types/api.types.ts` 定義 API 通用類型 (PaginationResponse, ApiError)
  - _Requirements: 1.3_

- [ ] 3. 實作 API 服務層
- [ ] 3.1 配置 Axios 實例與攔截器
  - 建立 `services/api.ts` 配置 Axios 實例
  - 實作請求攔截器自動附加 JWT Token
  - 實作響應攔截器處理錯誤 (401, 403, 404, 422, 500)
  - 實作錯誤通知機制
  - _Requirements: 1.6, 13.2, 13.7_

- [ ] 3.2 實作 Ticket Service
  - 建立 `services/ticket.service.ts`
  - 實作 `getTickets()` 查詢工單列表
  - 實作 `getTicketById()` 和 `getTicketByTicketNo()` 取得單一工單
  - 實作 `createTicket()` 建立工單
  - 實作 `updateTicket()` 更新工單
  - 實作 `updateTicketStatus()` 變更工單狀態
  - 實作 `getTicketNotes()` 和 `addTicketNote()` 處理時間軸
  - _Requirements: 4.7, 5.1, 6.1_

- [ ] 3.3 實作其他 API Services
  - 建立 `services/template.service.ts` 實作範本相關 API
  - 建立 `services/approval.service.ts` 實作簽核相關 API
  - 建立 `services/category.service.ts` 實作分類相關 API
  - 建立 `services/label.service.ts` 實作標籤相關 API
  - 建立 `services/attachment.service.ts` 實作附件上傳/下載 API
  - _Requirements: 3.1, 7.1, 8.1, 10.1_


- [ ] 4. 建立 Pinia Stores
- [ ] 4.1 實作 Auth Store
  - 建立 `stores/auth.store.ts`
  - 實作 `login()` 登入功能
  - 實作 `logout()` 登出功能
  - 實作 `fetchCurrentUser()` 取得當前使用者資訊
  - 實作 `isAuthenticated` computed 屬性
  - 處理 Token 的 localStorage 儲存
  - _Requirements: 1.6_

- [ ] 4.2 實作 Ticket Store
  - 建立 `stores/ticket.store.ts`
  - 實作 `fetchTickets()` 查詢工單列表
  - 實作 `fetchTicketById()` 取得單一工單
  - 實作 `createTicket()` 建立工單
  - 實作 `updateTicket()` 更新工單
  - 管理 tickets、currentTicket、loading、pagination 狀態
  - _Requirements: 5.1, 6.1_

- [ ] 4.3 實作其他 Stores
  - 建立 `stores/template.store.ts` 管理範本狀態
  - 建立 `stores/approval.store.ts` 管理簽核狀態
  - 建立 `stores/category.store.ts` 管理分類狀態
  - 建立 `stores/label.store.ts` 管理標籤狀態
  - 建立 `stores/ui.store.ts` 管理 UI 狀態 (theme, locale, drawer, notifications)
  - _Requirements: 12.1, 12.6, 15.1_

- [ ] 5. 配置路由系統
- [ ] 5.1 建立路由配置
  - 建立 `router/routes.ts` 定義所有路由
  - 配置前台路由 (Home, TicketList, TicketDetail, TicketCreate, TemplateGallery, ApprovalList)
  - 配置後台路由 (TemplateManagement, ApprovalTemplateManagement, CategoryManagement, LabelManagement)
  - 配置錯誤頁面路由 (NotFound, Forbidden)
  - 使用懶載入優化路由組件
  - _Requirements: 11.1, 11.2, 11.6, 14.2_

- [ ] 5.2 實作路由守衛
  - 建立 `router/guards.ts`
  - 實作認證守衛檢查使用者登入狀態
  - 實作管理員權限守衛
  - 實作頁面標題設定
  - _Requirements: 11.7, 13.7_

- [ ] 6. 建立佈局組件
- [ ] 6.1 實作 DefaultLayout
  - 建立 `layouts/DefaultLayout.vue`
  - 整合 AppBar 和 NavigationDrawer
  - 實作響應式佈局 (桌面版和行動版)
  - _Requirements: 11.1, 12.3, 12.4, 12.5_

- [ ] 6.2 實作 AppBar 組件
  - 建立 `components/layout/AppBar.vue`
  - 顯示 Logo 和應用程式標題
  - 實作主選單按鈕 (行動版)
  - 實作通知圖示和下拉選單
  - 實作使用者頭像和選單 (個人資料、設定、登出)
  - _Requirements: 11.1, 11.4, 11.5_

- [ ] 6.3 實作 NavigationDrawer 組件
  - 建立 `components/layout/NavigationDrawer.vue`
  - 實作選單項目 (Tickets, Approvals, Templates, Categories, Labels)
  - 實作當前路由高亮
  - 實作管理功能入口 (僅管理員可見)
  - 實作響應式收合功能
  - _Requirements: 11.2, 11.3, 11.6_


- [ ] 7. 建立通用 UI 組件
- [ ] 7.1 實作基礎組件
  - 建立 `components/common/LoadingSpinner.vue` 載入動畫組件
  - 建立 `components/common/EmptyState.vue` 空狀態提示組件
  - 建立 `components/common/AppDialog.vue` 對話框組件
  - 為組件編寫單元測試
  - _Requirements: 5.7, 13.5_

- [ ] 7.2 實作狀態徽章組件
  - 建立 `components/ticket/TicketStatusBadge.vue` 顯示工單狀態
  - 建立 `components/ticket/TicketPriorityBadge.vue` 顯示優先級
  - 使用不同顏色區分狀態和優先級
  - 為組件編寫單元測試
  - _Requirements: 5.2_

- [ ] 8. 實作首頁
- [ ] 8.1 建立 Home 頁面
  - 建立 `views/Home.vue`
  - 顯示歡迎訊息「Create Your Request In Seconds」
  - 實作「Create New Ticket」和「Browse Templates」按鈕
  - 實作「Popular Templates」區塊顯示常用範本
  - 實作範本卡片點擊導航
  - 為頁面編寫組件測試
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_

- [ ] 8.2 建立 TemplateCard 組件
  - 建立 `components/template/TemplateCard.vue`
  - 顯示範本名稱、描述、分類標籤
  - 使用彩色徽章顯示分類
  - 實作點擊事件
  - 為組件編寫單元測試
  - _Requirements: 2.4_

- [ ] 9. 實作範本瀏覽頁面
- [ ] 9.1 建立 TemplateGallery 頁面
  - 建立 `views/template/TemplateGallery.vue`
  - 顯示標題「Template Gallery」和副標題
  - 整合搜尋框和分類篩選器
  - 實作範本卡片網格佈局
  - 實作即時搜尋和篩選功能
  - 為頁面編寫組件測試
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

- [ ] 9.2 建立 TemplateCategoryFilter 組件
  - 建立 `components/template/TemplateCategoryFilter.vue`
  - 顯示所有分類及其工單數量
  - 實作分類選擇功能
  - 實作選中狀態高亮
  - 為組件編寫單元測試
  - _Requirements: 3.3, 3.4_

- [ ] 10. 實作工單建立表單
- [ ] 10.1 建立 TicketCreate 頁面
  - 建立 `views/ticket/TicketCreate.vue`
  - 整合 TicketForm 組件
  - 處理表單提交邏輯
  - 實作成功後導航至工單詳情頁面
  - 實作錯誤處理和使用者回饋
  - 為頁面編寫組件測試
  - _Requirements: 4.7, 4.8, 4.9_

- [ ] 10.2 建立 TicketForm 組件
  - 建立 `components/ticket/TicketForm.vue`
  - 實作標題、描述、優先級、可見性、截止日期欄位
  - 整合 RichTextEditor 用於描述欄位
  - 整合 FileUpload 用於附件上傳
  - 整合 TagSelector 用於標籤選擇
  - 實作範本預填功能
  - 實作即時表單驗證
  - 為組件編寫單元測試
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_


- [ ] 10.3 建立表單子組件
  - 建立 `components/form/RichTextEditor.vue` 富文本編輯器 (使用 Tiptap 或 Quill)
  - 建立 `components/form/FileUpload.vue` 檔案上傳組件 (支援拖放和進度顯示)
  - 建立 `components/form/TagSelector.vue` 標籤選擇器 (支援多選和搜尋)
  - 建立 `components/form/CustomFieldRenderer.vue` 自訂欄位渲染器
  - 為組件編寫單元測試
  - _Requirements: 4.3, 4.5, 4.6_

- [ ] 11. 實作工單列表頁面
- [ ] 11.1 建立 TicketList 頁面
  - 建立 `views/ticket/TicketList.vue`
  - 整合 TicketFilters 和 TicketList 組件
  - 實作分頁功能
  - 實作排序功能
  - 實作空狀態顯示
  - 為頁面編寫組件測試
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

- [ ] 11.2 建立 TicketFilters 組件
  - 建立 `components/ticket/TicketFilters.vue`
  - 實作狀態、優先級、分類、標籤篩選器
  - 實作即時篩選功能
  - 實作篩選條件清除功能
  - 為組件編寫單元測試
  - _Requirements: 5.3, 5.4_

- [ ] 11.3 建立 TicketList 組件
  - 建立 `components/ticket/TicketList.vue`
  - 使用 TicketCard 組件顯示工單
  - 實作網格或列表佈局切換
  - 實作虛擬滾動優化 (如果需要)
  - 為組件編寫單元測試
  - _Requirements: 5.2, 14.3_

- [ ] 12. 實作工單詳情頁面
- [ ] 12.1 建立 TicketDetail 頁面
  - 建立 `views/ticket/TicketDetail.vue`
  - 顯示工單基本資訊 (標題、描述、狀態、優先級等)
  - 實作右側元資訊面板 (建立者、建立時間、更新時間、指派人員)
  - 顯示附件列表並支援下載
  - 顯示標籤徽章
  - 整合 TicketTimeline 組件
  - 實作狀態變更按鈕 (根據權限顯示)
  - 為頁面編寫組件測試
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.10_

- [ ] 12.2 建立 TicketTimeline 組件
  - 建立 `components/ticket/TicketTimeline.vue`
  - 顯示統一時間軸 (留言和系統事件)
  - 區分使用者留言和系統事件的視覺樣式
  - 實作留言輸入框
  - 實作留言附件上傳
  - 實作留言提交和即時更新
  - 為組件編寫單元測試
  - _Requirements: 6.5, 6.6, 6.7, 6.8_

- [ ] 12.3 整合簽核流程顯示
  - 建立 `components/approval/ApprovalProgress.vue` 顯示簽核進度
  - 顯示簽核流程步驟和當前簽核人
  - 顯示各步驟的狀態 (pending, approved, rejected)
  - 為組件編寫單元測試
  - _Requirements: 6.9_

- [ ] 13. 實作簽核功能
- [ ] 13.1 建立 ApprovalList 頁面
  - 建立 `views/approval/ApprovalList.vue`
  - 顯示待簽核工單列表
  - 實作點擊導航至工單詳情
  - 顯示簽核數量徽章在導航列
  - 為頁面編寫組件測試
  - _Requirements: 7.1, 7.2_


- [ ] 13.2 建立簽核操作組件
  - 建立 `components/approval/ApprovalActionDialog.vue` 簽核操作對話框
  - 實作核准操作 (可選填留言)
  - 實作駁回操作 (必填駁回原因)
  - 實作確認對話框
  - 實作 API 呼叫和狀態更新
  - 為組件編寫單元測試
  - _Requirements: 7.3, 7.4, 7.5, 7.6, 7.7_

- [ ] 14. 實作後台管理 - 範本管理
- [ ] 14.1 建立 TemplateManagement 頁面
  - 建立 `views/admin/TemplateManagement.vue`
  - 顯示範本列表
  - 實作「新增範本」按鈕
  - 實作範本編輯和刪除功能
  - 實作確認對話框
  - 為頁面編寫組件測試
  - _Requirements: 8.1, 8.2, 8.7, 8.8_

- [ ] 14.2 建立範本表單組件
  - 建立範本建立/編輯表單
  - 實作名稱、描述、分類、標籤欄位
  - 實作自訂欄位配置器 (支援多種欄位類型)
  - 實作簽核範本選擇器
  - 實作表單驗證
  - 為組件編寫單元測試
  - _Requirements: 8.3, 8.4, 8.5, 8.6_

- [ ] 15. 實作後台管理 - 簽核範本管理
- [ ] 15.1 建立 ApprovalTemplateManagement 頁面
  - 建立 `views/admin/ApprovalTemplateManagement.vue`
  - 顯示簽核範本列表
  - 實作「新增簽核範本」按鈕
  - 實作簽核範本編輯和刪除功能
  - 實作使用檢查和警告
  - 為頁面編寫組件測試
  - _Requirements: 9.1, 9.2, 9.8, 9.9_

- [ ] 15.2 建立簽核範本表單組件
  - 建立簽核範本建立/編輯表單
  - 實作簽核步驟新增功能
  - 實作簽核類型選擇 (會簽/或簽)
  - 實作簽核人指定 (使用者或角色)
  - 實作步驟順序調整
  - 實作表單驗證
  - 為組件編寫單元測試
  - _Requirements: 9.3, 9.4, 9.5, 9.6, 9.7_

- [ ] 16. 實作後台管理 - 分類與標籤管理
- [ ] 16.1 建立 CategoryManagement 頁面
  - 建立 `views/admin/CategoryManagement.vue`
  - 顯示分類列表
  - 實作新增、編輯、刪除分類功能
  - 實作使用檢查和警告
  - 為頁面編寫組件測試
  - _Requirements: 10.1, 10.3, 10.7, 10.8_

- [ ] 16.2 建立 LabelManagement 頁面
  - 建立 `views/admin/LabelManagement.vue`
  - 顯示標籤列表
  - 實作新增、編輯、刪除標籤功能
  - 實作顏色選擇器並即時預覽
  - 實作使用檢查和警告
  - 為頁面編寫組件測試
  - _Requirements: 10.2, 10.4, 10.5, 10.7, 10.8_

- [ ] 17. 實作國際化 (i18n)
- [ ] 17.1 配置 Vue I18n
  - 建立 `plugins/i18n.ts` 配置 Vue I18n
  - 建立 `locales/zh-TW.ts` 繁體中文翻譯檔案
  - 建立 `locales/en.ts` 英文翻譯檔案
  - 實作語言切換功能
  - 實作語言偏好設定儲存
  - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.7_


- [ ] 17.2 實作日期和數字格式化
  - 建立 `utils/date.ts` 實作日期格式化工具函數
  - 實作根據語言設定格式化日期時間
  - 實作根據地區設定格式化數字
  - 為工具函數編寫單元測試
  - _Requirements: 15.5, 15.6_

- [ ] 18. 實作主題系統
- [ ] 18.1 配置 Vuetify 主題
  - 建立 `plugins/vuetify.ts` 配置 Vuetify
  - 配置深色主題作為預設主題
  - 配置紫色作為主要品牌色
  - 配置淺色主題
  - 實作主題切換功能
  - 實作主題偏好設定儲存
  - _Requirements: 12.1, 12.2, 12.6, 12.7_

- [ ] 19. 實作響應式設計
- [ ] 19.1 實作響應式佈局
  - 使用 Vuetify 的響應式斷點系統
  - 實作桌面版完整佈局
  - 實作平板版調整佈局
  - 實作行動版漢堡選單和調整卡片佈局
  - 測試各種裝置尺寸
  - _Requirements: 12.3, 12.4, 12.5_

- [ ] 20. 實作錯誤處理與使用者回饋
- [ ] 20.1 建立通知系統
  - 建立 `composables/useNotification.ts` 實作通知 composable
  - 使用 Vuetify Snackbar 顯示通知
  - 實作成功、錯誤、警告、資訊四種類型通知
  - 整合到 API 錯誤攔截器
  - _Requirements: 13.1, 13.2_

- [ ] 20.2 建立錯誤頁面
  - 建立 `views/error/NotFound.vue` 404 錯誤頁面
  - 建立 `views/error/Forbidden.vue` 403 錯誤頁面
  - 實作返回連結
  - 為頁面編寫組件測試
  - _Requirements: 13.7_

- [ ] 20.3 實作表單驗證
  - 配置 Vee-Validate 和 Yup
  - 建立 `utils/validation.ts` 定義驗證 schemas
  - 實作即時表單驗證
  - 實作錯誤訊息顯示
  - _Requirements: 13.3_

- [ ] 20.4 實作載入狀態和離線提示
  - 實作 API 請求載入動畫
  - 實作骨架屏 (Skeleton Loader)
  - 實作網路連線中斷提示
  - 實作確認對話框
  - _Requirements: 13.4, 13.5, 13.6_

- [ ] 21. 實作效能優化
- [ ] 21.1 實作程式碼分割和懶載入
  - 配置路由懶載入
  - 配置大型組件懶載入
  - 配置 Vite 建置優化
  - 實作 manual chunks 分割
  - 測試首屏載入時間
  - _Requirements: 14.1, 14.2, 14.7_

- [ ] 21.2 實作列表優化
  - 實作分頁功能
  - 評估並實作虛擬滾動 (如果需要)
  - 實作無限滾動 (時間軸)
  - 測試大量資料載入效能
  - _Requirements: 14.3_

- [ ] 21.3 實作圖片和資源優化
  - 實作圖片懶載入
  - 配置圖片壓縮
  - 優化字體載入
  - 使用 SVG 圖示
  - _Requirements: 14.4_


- [ ] 21.4 實作 API 請求優化
  - 實作搜尋輸入去抖 (Debounce)
  - 實作滾動載入節流 (Throttle)
  - 實作 Pinia store 資料快取
  - 實作樂觀更新
  - _Requirements: 14.5, 14.6_

- [ ] 22. 實作可訪問性 (a11y)
- [ ] 22.1 實作語義化 HTML 和 ARIA
  - 使用正確的 HTML 標籤
  - 為表單標籤使用 `<label>` 關聯
  - 為互動元素添加 ARIA 屬性
  - 為圖片提供 alt 文字
  - 為按鈕提供 aria-label
  - 測試螢幕閱讀器相容性
  - _Requirements: 12.7_

- [ ] 22.2 實作鍵盤導航和焦點管理
  - 確保所有互動元素可用 Tab 鍵訪問
  - 實作對話框 Esc 鍵關閉
  - 實作下拉選單方向鍵導航
  - 實作對話框焦點管理
  - 測試鍵盤導航流程
  - _Requirements: 12.7_

- [ ] 22.3 實作顏色對比和高對比度模式
  - 確保文字與背景對比度至少 4.5:1
  - 不僅依賴顏色傳達資訊
  - 評估並實作高對比度模式 (如果需要)
  - 測試顏色對比度
  - _Requirements: 12.7_

- [ ] 23. 編寫測試
- [ ] 23.1 編寫單元測試
  - 為 utils 中的工具函數編寫測試
  - 為 composables 編寫測試
  - 為 stores 的 actions 和 getters 編寫測試
  - 達到 80%+ 覆蓋率目標
  - _Requirements: 所有功能需求_

- [ ] 23.2 編寫組件測試
  - 為通用組件編寫測試
  - 為表單組件編寫測試
  - 為工單相關組件編寫測試
  - 達到 70%+ 覆蓋率目標
  - _Requirements: 所有功能需求_

- [ ] 23.3 編寫端對端測試
  - 使用 Playwright 或 Cypress 編寫 E2E 測試
  - 測試工單建立流程
  - 測試工單列表和詳情流程
  - 測試簽核流程
  - 測試管理功能流程
  - _Requirements: 所有功能需求_

- [ ] 24. 配置部署環境
- [ ] 24.1 配置環境變數
  - 建立 `.env.development` 開發環境變數
  - 建立 `.env.production` 生產環境變數
  - 配置 API 基礎 URL
  - 配置應用程式標題
  - _Requirements: 14.7_

- [ ] 24.2 建立 Docker 配置
  - 建立 `Dockerfile` 多階段建置
  - 建立 `nginx.conf` Nginx 配置
  - 配置 Gzip 壓縮
  - 配置 SPA 路由支援
  - 配置靜態資源快取
  - 測試 Docker 建置和執行
  - _Requirements: 14.7_

- [ ] 25. 整合測試與文件
- [ ] 25.1 整合測試
  - 執行所有單元測試
  - 執行所有組件測試
  - 執行所有 E2E 測試
  - 檢查測試覆蓋率
  - 修復失敗的測試
  - _Requirements: 所有功能需求_

- [ ] 25.2 編寫專案文件
  - 更新 README.md 包含專案說明、安裝步驟、開發指南
  - 建立 API 文件說明如何與後端整合
  - 建立組件文件說明主要組件的使用方式
  - 建立部署文件說明部署流程
  - _Requirements: 所有功能需求_
