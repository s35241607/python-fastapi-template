# Design Document

## Overview

本設計文件定義企業級智慧工單系統前端應用程式的技術架構與實作細節。系統採用 Vue 3 + Vite + Vuetify + Pinia 技術棧，提供現代化的單頁應用程式 (SPA) 體驗，並與後端 FastAPI 服務進行 RESTful API 通訊。

### 技術棧

- **框架**: Vue 3 (Composition API with `<script setup>`)
- **建置工具**: Vite 5+
- **語言**: TypeScript 5+
- **UI 框架**: Vuetify 3 (Material Design)
- **狀態管理**: Pinia
- **路由**: Vue Router 4
- **HTTP 客戶端**: Axios
- **表單驗證**: Vee-Validate + Yup
- **富文本編輯器**: Tiptap 或 Quill
- **國際化**: Vue I18n
- **日期處理**: Day.js

### 設計原則

1. **組件化設計**: 採用原子設計 (Atomic Design) 方法論，建立可重用的 UI 組件
2. **類型安全**: 全面使用 TypeScript 確保類型安全
3. **響應式優先**: Mobile-first 設計，確保在所有裝置上的良好體驗
4. **效能優化**: 使用懶載入、虛擬滾動、程式碼分割等技術
5. **可訪問性**: 遵循 WCAG 2.1 AA 標準
6. **一致性**: 統一的設計語言和使用者體驗

## Architecture

### 專案結構


```
ticket-system-frontend/
├── public/                      # 靜態資源
│   └── favicon.ico
├── src/
│   ├── assets/                  # 圖片、字體等資源
│   │   ├── images/
│   │   └── styles/
│   │       └── variables.scss   # 全域樣式變數
│   ├── components/              # 可重用組件
│   │   ├── common/              # 通用組件
│   │   │   ├── AppButton.vue
│   │   │   ├── AppCard.vue
│   │   │   ├── AppDialog.vue
│   │   │   ├── LoadingSpinner.vue
│   │   │   └── EmptyState.vue
│   │   ├── layout/              # 佈局組件
│   │   │   ├── AppBar.vue
│   │   │   ├── NavigationDrawer.vue
│   │   │   ├── UserMenu.vue
│   │   │   └── NotificationMenu.vue
│   │   ├── ticket/              # 工單相關組件
│   │   │   ├── TicketCard.vue
│   │   │   ├── TicketList.vue
│   │   │   ├── TicketForm.vue
│   │   │   ├── TicketFilters.vue
│   │   │   ├── TicketStatusBadge.vue
│   │   │   ├── TicketPriorityBadge.vue
│   │   │   └── TicketTimeline.vue
│   │   ├── template/            # 範本相關組件
│   │   │   ├── TemplateCard.vue
│   │   │   ├── TemplateGallery.vue
│   │   │   └── TemplateCategoryFilter.vue
│   │   ├── approval/            # 簽核相關組件
│   │   │   ├── ApprovalProgress.vue
│   │   │   ├── ApprovalStepCard.vue
│   │   │   └── ApprovalActionDialog.vue
│   │   └── form/                # 表單組件
│   │       ├── RichTextEditor.vue
│   │       ├── FileUpload.vue
│   │       ├── TagSelector.vue
│   │       └── CustomFieldRenderer.vue
│   ├── composables/             # 可組合函數
│   │   ├── useApi.ts
│   │   ├── useAuth.ts
│   │   ├── useNotification.ts
│   │   ├── useDialog.ts
│   │   └── usePermission.ts
│   ├── layouts/                 # 頁面佈局
│   │   ├── DefaultLayout.vue
│   │   ├── AdminLayout.vue
│   │   └── EmptyLayout.vue
│   ├── plugins/                 # Vue 插件
│   │   ├── vuetify.ts
│   │   ├── i18n.ts
│   │   └── router.ts
│   ├── router/                  # 路由配置
│   │   ├── index.ts
│   │   ├── routes.ts
│   │   └── guards.ts
│   ├── services/                # API 服務層
│   │   ├── api.ts               # Axios 實例配置
│   │   ├── ticket.service.ts
│   │   ├── template.service.ts
│   │   ├── approval.service.ts
│   │   ├── category.service.ts
│   │   ├── label.service.ts
│   │   ├── attachment.service.ts
│   │   └── auth.service.ts
│   ├── stores/                  # Pinia stores
│   │   ├── auth.store.ts
│   │   ├── ticket.store.ts
│   │   ├── template.store.ts
│   │   ├── approval.store.ts
│   │   ├── category.store.ts
│   │   ├── label.store.ts
│   │   └── ui.store.ts
│   ├── types/                   # TypeScript 類型定義
│   │   ├── ticket.types.ts
│   │   ├── template.types.ts
│   │   ├── approval.types.ts
│   │   ├── category.types.ts
│   │   ├── label.types.ts
│   │   ├── attachment.types.ts
│   │   ├── user.types.ts
│   │   └── api.types.ts
│   ├── utils/                   # 工具函數
│   │   ├── date.ts
│   │   ├── validation.ts
│   │   ├── format.ts
│   │   └── constants.ts
│   ├── views/                   # 頁面組件
│   │   ├── Home.vue
│   │   ├── ticket/
│   │   │   ├── TicketList.vue
│   │   │   ├── TicketDetail.vue
│   │   │   └── TicketCreate.vue
│   │   ├── template/
│   │   │   ├── TemplateGallery.vue
│   │   │   └── TemplateDetail.vue
│   │   ├── approval/
│   │   │   └── ApprovalList.vue
│   │   ├── admin/
│   │   │   ├── TemplateManagement.vue
│   │   │   ├── ApprovalTemplateManagement.vue
│   │   │   ├── CategoryManagement.vue
│   │   │   └── LabelManagement.vue
│   │   └── error/
│   │       ├── NotFound.vue
│   │       └── Forbidden.vue
│   ├── App.vue
│   └── main.ts
├── .env.development             # 開發環境變數
├── .env.production              # 生產環境變數
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

### 架構層次


1. **展示層 (Presentation Layer)**: Views 和 Components
2. **業務邏輯層 (Business Logic Layer)**: Stores 和 Composables
3. **資料存取層 (Data Access Layer)**: Services
4. **工具層 (Utility Layer)**: Utils 和 Types

### 資料流

```
User Interaction → Component → Store (Pinia) → Service → API (Backend)
                                  ↓
                            Local State Update
                                  ↓
                            Component Re-render
```

## Components and Interfaces

### 核心組件設計

#### 1. Layout Components

**AppBar.vue**
- 功能: 頂部導航列
- Props: `title`, `showMenu`, `showNotifications`
- Emits: `menu-click`, `notification-click`
- 包含: Logo、主選單、通知圖示、使用者頭像

**NavigationDrawer.vue**
- 功能: 側邊導航選單
- Props: `modelValue` (boolean), `items` (NavigationItem[])
- Emits: `update:modelValue`
- 響應式: 桌面版常駐，行動版可收合

#### 2. Ticket Components

**TicketCard.vue**
- 功能: 工單卡片展示
- Props: `ticket` (Ticket), `compact` (boolean)
- Emits: `click`
- 顯示: 工單編號、標題、狀態、優先級、建立時間、標籤

**TicketForm.vue**
- 功能: 工單建立/編輯表單
- Props: `ticket` (Ticket | null), `template` (TicketTemplate | null)
- Emits: `submit`, `cancel`
- 包含: 標題、描述 (富文本)、優先級、可見性、截止日期、附件上傳、標籤選擇、自訂欄位

**TicketTimeline.vue**
- 功能: 統一時間軸顯示
- Props: `ticketId` (number)
- 顯示: 使用者留言和系統事件，區分視覺樣式
- 功能: 新增留言、附件上傳


#### 3. Template Components

**TemplateCard.vue**
- 功能: 範本卡片展示
- Props: `template` (TicketTemplate)
- Emits: `click`, `use-template`
- 顯示: 範本名稱、描述、分類標籤

**TemplateGallery.vue**
- 功能: 範本瀏覽網格
- Props: `templates` (TicketTemplate[]), `loading` (boolean)
- Emits: `template-select`
- 包含: 搜尋框、分類篩選器、範本卡片網格

#### 4. Approval Components

**ApprovalProgress.vue**
- 功能: 簽核流程進度顯示
- Props: `approvalProcess` (ApprovalProcess)
- 顯示: 步驟進度條、當前簽核人、各步驟狀態

**ApprovalActionDialog.vue**
- 功能: 簽核操作對話框
- Props: `step` (ApprovalProcessStep), `action` ('approve' | 'reject')
- Emits: `confirm`, `cancel`
- 包含: 留言輸入框 (核准可選，駁回必填)

#### 5. Form Components

**RichTextEditor.vue**
- 功能: 富文本編輯器
- Props: `modelValue` (string), `placeholder` (string)
- Emits: `update:modelValue`, `image-upload`
- 功能: 格式化文字、插入圖片、Markdown 支援

**FileUpload.vue**
- 功能: 檔案上傳組件
- Props: `multiple` (boolean), `accept` (string), `maxSize` (number)
- Emits: `upload`, `remove`
- 功能: 拖放上傳、進度顯示、檔案預覽

**TagSelector.vue**
- 功能: 標籤選擇器
- Props: `modelValue` (number[]), `availableTags` (Label[])
- Emits: `update:modelValue`
- 功能: 多選、搜尋、顏色顯示

### API Service 介面設計


#### Ticket Service

```typescript
interface TicketService {
  // 查詢工單列表
  getTickets(params: TicketQueryParams): Promise<PaginationResponse<Ticket>>;

  // 取得單一工單
  getTicketById(id: number): Promise<Ticket>;
  getTicketByTicketNo(ticketNo: string): Promise<Ticket>;

  // 建立工單
  createTicket(data: TicketCreate): Promise<Ticket>;

  // 更新工單
  updateTicket(id: number, data: TicketUpdate): Promise<Ticket>;

  // 變更工單狀態
  updateTicketStatus(id: number, status: TicketStatus, reason?: string): Promise<Ticket>;

  // 工單時間軸
  getTicketNotes(ticketId: number): Promise<TicketNote[]>;
  addTicketNote(ticketId: number, note: string, attachments?: number[]): Promise<TicketNote>;

  // 工單標籤
  getTicketLabels(ticketId: number): Promise<Label[]>;
  addTicketLabel(ticketId: number, labelId: number): Promise<void>;
  removeTicketLabel(ticketId: number, labelId: number): Promise<void>;

  // 工單權限
  getTicketPermissions(ticketId: number): Promise<TicketViewPermission[]>;
  addTicketPermission(ticketId: number, permission: TicketViewPermissionCreate): Promise<void>;
}
```

#### Template Service

```typescript
interface TemplateService {
  // 查詢範本列表
  getTemplates(params?: TemplateQueryParams): Promise<TicketTemplate[]>;

  // 取得單一範本
  getTemplateById(id: number): Promise<TicketTemplate>;

  // 建立範本 (管理員)
  createTemplate(data: TemplateCreate): Promise<TicketTemplate>;

  // 更新範本 (管理員)
  updateTemplate(id: number, data: TemplateUpdate): Promise<TicketTemplate>;

  // 刪除範本 (管理員)
  deleteTemplate(id: number): Promise<void>;
}
```

#### Approval Service

```typescript
interface ApprovalService {
  // 查詢待簽核列表
  getMyPendingApprovals(): Promise<ApprovalProcessStep[]>;

  // 核准簽核步驟
  approveStep(stepId: number, comment?: string): Promise<void>;

  // 駁回簽核步驟
  rejectStep(stepId: number, reason: string): Promise<void>;

  // 取得工單的簽核流程
  getApprovalProcess(ticketId: number): Promise<ApprovalProcess>;
}
```


#### Attachment Service

```typescript
interface AttachmentService {
  // 上傳附件
  uploadAttachment(file: File, relatedType: string, relatedId: number, usageType: AttachmentUsageType): Promise<Attachment>;

  // 批量上傳
  uploadAttachmentsBatch(files: File[], relatedType: string, relatedId: number, usageType: AttachmentUsageType): Promise<Attachment[]>;

  // 預上傳 (不關聯資源)
  preuploadAttachment(file: File, usageType: AttachmentUsageType): Promise<Attachment>;

  // 上傳富文本圖片
  uploadRichTextImage(file: File, relatedType: string, relatedId: number, altText?: string): Promise<{ attachment: Attachment; markdownSyntax: string }>;

  // 關聯預上傳的附件
  linkAttachments(attachmentIds: number[], relatedType: string, relatedId: number): Promise<Attachment[]>;

  // 取得附件列表
  getAttachments(relatedType: string, relatedId: number, usageType?: AttachmentUsageType): Promise<Attachment[]>;

  // 下載附件
  downloadAttachment(attachmentId: number): Promise<Blob>;

  // 刪除附件
  deleteAttachment(attachmentId: number): Promise<void>;
}
```

## Data Models

### TypeScript 類型定義

#### Ticket Types

```typescript
enum TicketStatus {
  DRAFT = 'draft',
  WAITING_APPROVAL = 'waiting_approval',
  REJECTED = 'rejected',
  OPEN = 'open',
  IN_PROGRESS = 'in_progress',
  RESOLVED = 'resolved',
  CLOSED = 'closed',
  CANCELLED = 'cancelled'
}

enum TicketPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  URGENT = 'urgent'
}

enum TicketVisibility {
  INTERNAL = 'internal',
  RESTRICTED = 'restricted'
}

interface Ticket {
  id: number;
  ticket_no: string;
  title: string;
  description: string | null;
  status: TicketStatus;
  priority: TicketPriority;
  visibility: TicketVisibility;
  due_date: string | null;
  assigned_to: number | null;
  ticket_template_id: number | null;
  approval_template_id: number | null;
  custom_fields_data: Record<string, any> | null;
  created_by: number;
  created_at: string;
  updated_by: number | null;
  updated_at: string | null;
  categories: Category[];
  labels: Label[];
}
```


```typescript
interface TicketCreate {
  title: string;
  description?: string;
  priority: TicketPriority;
  visibility: TicketVisibility;
  due_date?: string;
  assigned_to?: number;
  ticket_template_id?: number;
  approval_template_id?: number;
  custom_fields_data?: Record<string, any>;
  category_ids: number[];
  label_ids: number[];
}

interface TicketQueryParams {
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  status?: TicketStatus;
  priority?: TicketPriority;
  visibility?: TicketVisibility;
  assigned_to?: number;
  created_by?: number;
  ticket_template_id?: number;
  approval_template_id?: number;
}
```

#### Template Types

```typescript
interface TicketTemplate {
  id: number;
  name: string;
  description: string | null;
  default_title: string | null;
  default_description: string | null;
  default_priority: TicketPriority;
  default_visibility: TicketVisibility;
  custom_fields_schema: CustomFieldSchema[] | null;
  approval_template_id: number | null;
  is_active: boolean;
  created_at: string;
  categories: Category[];
  labels: Label[];
}

interface CustomFieldSchema {
  name: string;
  label: string;
  type: 'text' | 'number' | 'date' | 'select' | 'multiselect' | 'textarea';
  required: boolean;
  options?: string[];
  default_value?: any;
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
  };
}
```

#### Approval Types

```typescript
enum ApprovalProcessStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  REJECTED = 'rejected'
}

enum ApprovalStepType {
  ALL = 'all',  // 會簽
  ANY = 'any'   // 或簽
}

interface ApprovalProcess {
  id: number;
  ticket_id: number;
  approval_template_id: number;
  status: ApprovalProcessStatus;
  current_step: number;
  created_at: string;
  completed_at: string | null;
  steps: ApprovalProcessStep[];
}

interface ApprovalProcessStep {
  id: number;
  approval_process_id: number;
  step_order: number;
  step_type: ApprovalStepType;
  status: ApprovalProcessStatus;
  approver_id: number | null;
  proxy_id: number | null;
  approved_at: string | null;
  comment: string | null;
}
```


#### Other Types

```typescript
interface Category {
  id: number;
  name: string;
  description: string | null;
  created_at: string;
}

interface Label {
  id: number;
  name: string;
  color: string;  // Hex color code
  description: string | null;
  created_at: string;
}

interface Attachment {
  id: number;
  file_name: string;
  original_file_name: string;
  mime_type: string;
  file_size: number;
  storage_path: string;
  related_type: string;
  related_id: number;
  usage_type: AttachmentUsageType;
  description: string | null;
  created_at: string;
}

interface TicketNote {
  id: number;
  ticket_id: number;
  user_id: number | null;
  note: string | null;
  system: boolean;
  event_type: TicketEventType | null;
  event_details: Record<string, any> | null;
  created_at: string;
}

interface PaginationResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
```

## Error Handling

### 錯誤處理策略

#### 1. API 錯誤攔截器

在 Axios 實例中配置全域錯誤攔截器:

```typescript
// services/api.ts
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    const { response } = error;

    if (!response) {
      // 網路錯誤
      showNotification('網路連線失敗，請檢查您的網路連線', 'error');
      return Promise.reject(error);
    }

    switch (response.status) {
      case 401:
        // 未授權，導向登入頁
        router.push('/login');
        break;
      case 403:
        // 無權限
        showNotification('您沒有權限執行此操作', 'error');
        break;
      case 404:
        // 資源不存在
        showNotification('請求的資源不存在', 'error');
        break;
      case 422:
        // 驗證錯誤
        handleValidationErrors(response.data.detail);
        break;
      case 500:
        // 伺服器錯誤
        showNotification('伺服器發生錯誤，請稍後再試', 'error');
        break;
      default:
        showNotification('發生未知錯誤', 'error');
    }

    return Promise.reject(error);
  }
);
```


#### 2. 表單驗證錯誤

使用 Vee-Validate 進行前端驗證:

```typescript
// utils/validation.ts
import * as yup from 'yup';

export const ticketSchema = yup.object({
  title: yup.string().required('標題為必填').max(200, '標題不能超過 200 字元'),
  description: yup.string().nullable(),
  priority: yup.string().oneOf(['low', 'medium', 'high', 'urgent']).required(),
  visibility: yup.string().oneOf(['internal', 'restricted']).required(),
  due_date: yup.date().nullable().min(new Date(), '截止日期不能早於今天'),
});
```

#### 3. 錯誤頁面

- **404 Not Found**: 資源不存在頁面
- **403 Forbidden**: 無權限訪問頁面
- **500 Server Error**: 伺服器錯誤頁面

#### 4. 使用者回饋機制

使用 Vuetify 的 Snackbar 組件顯示通知:

```typescript
// composables/useNotification.ts
export function useNotification() {
  const show = (message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info') => {
    // 顯示 Snackbar
  };

  return { show };
}
```

## Testing Strategy

### 測試層級

#### 1. 單元測試 (Unit Tests)

使用 Vitest 進行單元測試:

- **工具函數測試**: 測試 utils 中的純函數
- **Composables 測試**: 測試可組合函數的邏輯
- **Store 測試**: 測試 Pinia stores 的 actions 和 getters

```typescript
// Example: utils/date.spec.ts
import { describe, it, expect } from 'vitest';
import { formatDate, isOverdue } from './date';

describe('Date Utils', () => {
  it('should format date correctly', () => {
    const date = '2025-01-15T10:30:00Z';
    expect(formatDate(date)).toBe('2025-01-15 10:30');
  });

  it('should detect overdue dates', () => {
    const pastDate = '2024-01-01T00:00:00Z';
    expect(isOverdue(pastDate)).toBe(true);
  });
});
```

#### 2. 組件測試 (Component Tests)

使用 Vitest + Vue Test Utils:

- 測試組件的渲染輸出
- 測試使用者互動 (點擊、輸入等)
- 測試 props 和 emits

```typescript
// Example: components/ticket/TicketCard.spec.ts
import { mount } from '@vue/test-utils';
import { describe, it, expect } from 'vitest';
import TicketCard from './TicketCard.vue';

describe('TicketCard', () => {
  it('should render ticket information', () => {
    const ticket = {
      id: 1,
      ticket_no: 'TK-001',
      title: 'Test Ticket',
      status: 'open',
      priority: 'high'
    };

    const wrapper = mount(TicketCard, {
      props: { ticket }
    });

    expect(wrapper.text()).toContain('TK-001');
    expect(wrapper.text()).toContain('Test Ticket');
  });
});
```


#### 3. 端對端測試 (E2E Tests)

使用 Playwright 或 Cypress:

- 測試完整的使用者流程
- 測試關鍵業務場景

```typescript
// Example: e2e/ticket-creation.spec.ts
import { test, expect } from '@playwright/test';

test('should create a new ticket', async ({ page }) => {
  await page.goto('/tickets/create');

  await page.fill('[data-testid="ticket-title"]', 'New Ticket');
  await page.fill('[data-testid="ticket-description"]', 'Description');
  await page.selectOption('[data-testid="ticket-priority"]', 'high');

  await page.click('[data-testid="submit-button"]');

  await expect(page).toHaveURL(/\/tickets\/\d+/);
  await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
});
```

### 測試覆蓋率目標

- 工具函數: 90%+
- Composables: 80%+
- Stores: 80%+
- 組件: 70%+
- 整體: 75%+

## State Management

### Pinia Stores 設計

#### Auth Store

```typescript
// stores/auth.store.ts
export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null);
  const token = ref<string | null>(null);
  const isAuthenticated = computed(() => !!token.value);

  async function login(credentials: LoginCredentials) {
    const response = await authService.login(credentials);
    token.value = response.access_token;
    user.value = response.user;
    localStorage.setItem('token', response.access_token);
  }

  function logout() {
    token.value = null;
    user.value = null;
    localStorage.removeItem('token');
    router.push('/login');
  }

  async function fetchCurrentUser() {
    if (!token.value) return;
    user.value = await authService.getCurrentUser();
  }

  return { user, token, isAuthenticated, login, logout, fetchCurrentUser };
});
```

#### Ticket Store

```typescript
// stores/ticket.store.ts
export const useTicketStore = defineStore('ticket', () => {
  const tickets = ref<Ticket[]>([]);
  const currentTicket = ref<Ticket | null>(null);
  const loading = ref(false);
  const pagination = ref<PaginationMeta>({
    page: 1,
    page_size: 20,
    total: 0,
    total_pages: 0
  });

  async function fetchTickets(params: TicketQueryParams) {
    loading.value = true;
    try {
      const response = await ticketService.getTickets(params);
      tickets.value = response.items;
      pagination.value = {
        page: response.page,
        page_size: response.page_size,
        total: response.total,
        total_pages: response.total_pages
      };
    } finally {
      loading.value = false;
    }
  }

  async function fetchTicketById(id: number) {
    loading.value = true;
    try {
      currentTicket.value = await ticketService.getTicketById(id);
    } finally {
      loading.value = false;
    }
  }

  async function createTicket(data: TicketCreate) {
    const ticket = await ticketService.createTicket(data);
    tickets.value.unshift(ticket);
    return ticket;
  }

  return { tickets, currentTicket, loading, pagination, fetchTickets, fetchTicketById, createTicket };
});
```


#### UI Store

```typescript
// stores/ui.store.ts
export const useUIStore = defineStore('ui', () => {
  const theme = ref<'light' | 'dark'>('dark');
  const locale = ref<'zh-TW' | 'en'>('zh-TW');
  const drawerOpen = ref(true);
  const notifications = ref<Notification[]>([]);

  function toggleTheme() {
    theme.value = theme.value === 'light' ? 'dark' : 'light';
    localStorage.setItem('theme', theme.value);
  }

  function setLocale(newLocale: 'zh-TW' | 'en') {
    locale.value = newLocale;
    localStorage.setItem('locale', newLocale);
  }

  function toggleDrawer() {
    drawerOpen.value = !drawerOpen.value;
  }

  function addNotification(notification: Omit<Notification, 'id'>) {
    const id = Date.now();
    notifications.value.push({ ...notification, id });
    setTimeout(() => removeNotification(id), 5000);
  }

  function removeNotification(id: number) {
    const index = notifications.value.findIndex(n => n.id === id);
    if (index > -1) notifications.value.splice(index, 1);
  }

  return { theme, locale, drawerOpen, notifications, toggleTheme, setLocale, toggleDrawer, addNotification, removeNotification };
});
```

## Routing

### 路由配置

```typescript
// router/routes.ts
export const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@/layouts/DefaultLayout.vue'),
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('@/views/Home.vue'),
        meta: { title: '首頁' }
      },
      {
        path: 'tickets',
        name: 'TicketList',
        component: () => import('@/views/ticket/TicketList.vue'),
        meta: { title: '工單列表' }
      },
      {
        path: 'tickets/create',
        name: 'TicketCreate',
        component: () => import('@/views/ticket/TicketCreate.vue'),
        meta: { title: '建立工單' }
      },
      {
        path: 'tickets/:id',
        name: 'TicketDetail',
        component: () => import('@/views/ticket/TicketDetail.vue'),
        meta: { title: '工單詳情' }
      },
      {
        path: 'templates',
        name: 'TemplateGallery',
        component: () => import('@/views/template/TemplateGallery.vue'),
        meta: { title: '範本瀏覽' }
      },
      {
        path: 'approvals',
        name: 'ApprovalList',
        component: () => import('@/views/approval/ApprovalList.vue'),
        meta: { title: '待簽核' }
      }
    ]
  },
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAdmin: true },
    children: [
      {
        path: 'templates',
        name: 'AdminTemplates',
        component: () => import('@/views/admin/TemplateManagement.vue'),
        meta: { title: '範本管理' }
      },
      {
        path: 'approval-templates',
        name: 'AdminApprovalTemplates',
        component: () => import('@/views/admin/ApprovalTemplateManagement.vue'),
        meta: { title: '簽核範本管理' }
      },
      {
        path: 'categories',
        name: 'AdminCategories',
        component: () => import('@/views/admin/CategoryManagement.vue'),
        meta: { title: '分類管理' }
      },
      {
        path: 'labels',
        name: 'AdminLabels',
        component: () => import('@/views/admin/LabelManagement.vue'),
        meta: { title: '標籤管理' }
      }
    ]
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { layout: 'empty', title: '登入' }
  },
  {
    path: '/403',
    name: 'Forbidden',
    component: () => import('@/views/error/Forbidden.vue'),
    meta: { layout: 'empty', title: '無權限' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/NotFound.vue'),
    meta: { layout: 'empty', title: '頁面不存在' }
  }
];
```


### 路由守衛

```typescript
// router/guards.ts
export function setupRouterGuards(router: Router) {
  // 認證守衛
  router.beforeEach((to, from, next) => {
    const authStore = useAuthStore();

    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
      next({ name: 'Login', query: { redirect: to.fullPath } });
      return;
    }

    if (to.meta.requiresAdmin && !authStore.user?.is_admin) {
      next({ name: 'Forbidden' });
      return;
    }

    next();
  });

  // 設定頁面標題
  router.afterEach((to) => {
    const title = to.meta.title as string;
    document.title = title ? `${title} - 工單系統` : '工單系統';
  });
}
```

## UI/UX Design

### 主題配置

```typescript
// plugins/vuetify.ts
import { createVuetify } from 'vuetify';
import { aliases, mdi } from 'vuetify/iconsets/mdi';

export default createVuetify({
  theme: {
    defaultTheme: 'dark',
    themes: {
      dark: {
        dark: true,
        colors: {
          primary: '#9C27B0',      // 紫色
          secondary: '#7B1FA2',
          accent: '#E1BEE7',
          error: '#F44336',
          warning: '#FF9800',
          info: '#2196F3',
          success: '#4CAF50',
          background: '#121212',
          surface: '#1E1E1E',
          'on-surface': '#FFFFFF'
        }
      },
      light: {
        dark: false,
        colors: {
          primary: '#9C27B0',
          secondary: '#7B1FA2',
          accent: '#E1BEE7',
          error: '#F44336',
          warning: '#FF9800',
          info: '#2196F3',
          success: '#4CAF50',
          background: '#FAFAFA',
          surface: '#FFFFFF',
          'on-surface': '#000000'
        }
      }
    }
  },
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: { mdi }
  }
});
```

### 響應式斷點

- **xs**: < 600px (手機)
- **sm**: 600px - 960px (平板直向)
- **md**: 960px - 1264px (平板橫向)
- **lg**: 1264px - 1904px (桌面)
- **xl**: > 1904px (大螢幕)

### 設計規範

#### 間距系統

- **xs**: 4px
- **sm**: 8px
- **md**: 16px
- **lg**: 24px
- **xl**: 32px

#### 圓角

- **小**: 4px (按鈕、輸入框)
- **中**: 8px (卡片)
- **大**: 12px (對話框)

#### 陰影

- **低**: `0 2px 4px rgba(0,0,0,0.1)`
- **中**: `0 4px 8px rgba(0,0,0,0.15)`
- **高**: `0 8px 16px rgba(0,0,0,0.2)`


## Performance Optimization

### 1. 程式碼分割 (Code Splitting)

- 使用 Vue Router 的懶載入功能
- 按路由分割程式碼
- 動態 import 大型組件

```typescript
// 路由懶載入
const TicketDetail = () => import('@/views/ticket/TicketDetail.vue');

// 組件懶載入
const RichTextEditor = defineAsyncComponent(() => import('@/components/form/RichTextEditor.vue'));
```

### 2. 資源優化

- 圖片懶載入: 使用 `v-lazy` 指令
- 圖片壓縮: 使用 WebP 格式
- 字體優化: 使用 font-display: swap
- SVG 圖示: 使用 Vuetify 的 MDI 圖示集

### 3. 列表優化

- 虛擬滾動: 使用 `vue-virtual-scroller` 處理大量資料
- 分頁: 預設每頁 20 筆
- 無限滾動: 適用於時間軸等場景

```typescript
// 虛擬滾動範例
<RecycleScroller
  :items="tickets"
  :item-size="80"
  key-field="id"
  v-slot="{ item }"
>
  <TicketCard :ticket="item" />
</RecycleScroller>
```

### 4. API 請求優化

- 請求去抖 (Debounce): 搜尋輸入
- 請求節流 (Throttle): 滾動載入
- 請求快取: 使用 Pinia 快取常用資料
- 樂觀更新: 立即更新 UI，背景同步 API

```typescript
// 搜尋去抖
import { useDebounceFn } from '@vueuse/core';

const debouncedSearch = useDebounceFn((query: string) => {
  searchTickets(query);
}, 300);
```

### 5. 建置優化

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['vue', 'vue-router', 'pinia'],
          'vuetify': ['vuetify'],
          'editor': ['@tiptap/vue-3', '@tiptap/starter-kit']
        }
      }
    },
    chunkSizeWarningLimit: 1000
  },
  optimizeDeps: {
    include: ['vue', 'vue-router', 'pinia', 'vuetify']
  }
});
```

## Internationalization (i18n)

### 語言檔案結構

```typescript
// locales/zh-TW.ts
export default {
  common: {
    save: '儲存',
    cancel: '取消',
    delete: '刪除',
    edit: '編輯',
    create: '建立',
    search: '搜尋',
    filter: '篩選',
    loading: '載入中...',
    noData: '無資料'
  },
  ticket: {
    title: '工單',
    create: '建立工單',
    list: '工單列表',
    detail: '工單詳情',
    status: {
      draft: '草稿',
      waiting_approval: '待簽核',
      rejected: '已駁回',
      open: '待處理',
      in_progress: '處理中',
      resolved: '已解決',
      closed: '已結案',
      cancelled: '已取消'
    },
    priority: {
      low: '低',
      medium: '中',
      high: '高',
      urgent: '緊急'
    }
  },
  validation: {
    required: '{field} 為必填',
    maxLength: '{field} 不能超過 {max} 字元',
    minLength: '{field} 至少需要 {min} 字元',
    email: '請輸入有效的電子郵件地址'
  }
};
```

### i18n 配置

```typescript
// plugins/i18n.ts
import { createI18n } from 'vue-i18n';
import zhTW from '@/locales/zh-TW';
import en from '@/locales/en';

export default createI18n({
  legacy: false,
  locale: localStorage.getItem('locale') || 'zh-TW',
  fallbackLocale: 'zh-TW',
  messages: {
    'zh-TW': zhTW,
    'en': en
  }
});
```


## Security Considerations

### 1. 認證與授權

- JWT Token 儲存在 localStorage
- 每次 API 請求自動附加 Bearer Token
- Token 過期自動導向登入頁
- 路由守衛檢查權限

```typescript
// services/api.ts
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### 2. XSS 防護

- Vue 預設會轉義 HTML
- 富文本內容使用 DOMPurify 清理
- 避免使用 `v-html`，必要時先清理內容

```typescript
import DOMPurify from 'dompurify';

const sanitizedHtml = DOMPurify.sanitize(userInput);
```

### 3. CSRF 防護

- 使用 SameSite Cookie 屬性
- API 請求使用 CORS 配置
- 後端驗證 Origin 標頭

### 4. 敏感資料處理

- 不在前端儲存敏感資料
- 密碼輸入使用 `type="password"`
- 附件上傳前驗證檔案類型和大小

### 5. 內容安全政策 (CSP)

```html
<!-- index.html -->
<meta http-equiv="Content-Security-Policy"
      content="default-src 'self';
               script-src 'self' 'unsafe-inline';
               style-src 'self' 'unsafe-inline';
               img-src 'self' data: https:;">
```

## Accessibility (a11y)

### 1. 語義化 HTML

- 使用正確的 HTML 標籤 (`<button>`, `<nav>`, `<main>`)
- 表單標籤使用 `<label>` 關聯輸入框
- 使用 ARIA 屬性增強可訪問性

### 2. 鍵盤導航

- 所有互動元素可用 Tab 鍵訪問
- 對話框支援 Esc 鍵關閉
- 下拉選單支援方向鍵導航

### 3. 螢幕閱讀器支援

- 圖片提供 alt 文字
- 按鈕提供 aria-label
- 動態內容更新使用 aria-live

```vue
<button
  aria-label="關閉對話框"
  @click="closeDialog"
>
  <v-icon>mdi-close</v-icon>
</button>
```

### 4. 顏色對比

- 文字與背景對比度至少 4.5:1
- 不僅依賴顏色傳達資訊
- 提供高對比度模式

### 5. 焦點管理

- 對話框開啟時焦點移至對話框
- 對話框關閉時焦點返回觸發元素
- 使用 focus-visible 顯示焦點狀態

## Deployment

### 環境變數

```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_TITLE=工單系統 (開發)

# .env.production
VITE_API_BASE_URL=https://api.example.com/api/v1
VITE_APP_TITLE=工單系統
```

### 建置指令

```bash
# 開發模式
npm run dev

# 建置生產版本
npm run build

# 預覽生產版本
npm run preview

# 執行測試
npm run test

# 執行 E2E 測試
npm run test:e2e

# 程式碼檢查
npm run lint

# 類型檢查
npm run type-check
```

### Docker 部署

```dockerfile
# Dockerfile
FROM node:20-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```


### Nginx 配置

```nginx
# nginx.conf
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip 壓縮
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # SPA 路由支援
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 代理 (可選)
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # 快取靜態資源
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## Development Workflow

### 1. 專案初始化

```bash
# 使用 Vite 建立專案
npm create vite@latest ticket-system-frontend -- --template vue-ts

# 安裝依賴
cd ticket-system-frontend
npm install

# 安裝 Vuetify
npm install vuetify @mdi/font

# 安裝其他依賴
npm install pinia vue-router axios vue-i18n
npm install -D @types/node
```

### 2. Git 工作流程

- **main**: 生產環境分支
- **develop**: 開發分支
- **feature/***: 功能分支
- **bugfix/***: 錯誤修復分支

### 3. 程式碼規範

使用 ESLint + Prettier:

```json
// .eslintrc.json
{
  "extends": [
    "plugin:vue/vue3-recommended",
    "@vue/typescript/recommended",
    "prettier"
  ],
  "rules": {
    "vue/multi-word-component-names": "off",
    "@typescript-eslint/no-explicit-any": "warn"
  }
}
```

### 4. Commit 規範

使用 Conventional Commits:

- `feat`: 新功能
- `fix`: 錯誤修復
- `docs`: 文件更新
- `style`: 程式碼格式調整
- `refactor`: 重構
- `test`: 測試相關
- `chore`: 建置或工具相關

範例: `feat(ticket): add ticket creation form`

## API Integration

### Axios 實例配置

```typescript
// services/api.ts
import axios from 'axios';
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 請求攔截器
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 響應攔截器
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    // 錯誤處理邏輯
    return Promise.reject(error);
  }
);

export default apiClient;
```

### API 端點對應

| 功能 | 方法 | 端點 | 說明 |
|------|------|------|------|
| 工單列表 | GET | `/tickets` | 查詢工單列表 |
| 工單詳情 | GET | `/tickets/{id}` | 取得單一工單 |
| 建立工單 | POST | `/tickets` | 建立新工單 |
| 更新工單 | PUT | `/tickets/{id}` | 更新工單資訊 |
| 變更狀態 | PATCH | `/tickets/{id}/status` | 變更工單狀態 |
| 工單時間軸 | GET | `/tickets/{id}/notes` | 取得時間軸 |
| 新增留言 | POST | `/tickets/{id}/notes` | 新增留言 |
| 範本列表 | GET | `/ticket-templates` | 查詢範本列表 |
| 分類列表 | GET | `/categories` | 查詢分類列表 |
| 標籤列表 | GET | `/labels` | 查詢標籤列表 |
| 待簽核列表 | GET | `/approvals/my-pending` | 查詢待簽核 |
| 核准簽核 | POST | `/approval-process-steps/{id}/approve` | 核准簽核 |
| 駁回簽核 | POST | `/approval-process-steps/{id}/reject` | 駁回簽核 |
| 上傳附件 | POST | `/attachments/upload` | 上傳附件 |

## Summary

本設計文件定義了企業級智慧工單系統前端應用程式的完整技術架構，包括:

1. **技術棧**: Vue 3 + Vite + Vuetify + Pinia + TypeScript
2. **架構設計**: 清晰的分層架構和模組化組件設計
3. **資料模型**: 完整的 TypeScript 類型定義
4. **狀態管理**: 使用 Pinia 進行集中式狀態管理
5. **路由設計**: 前台和後台分離的路由結構
6. **UI/UX**: 深色主題、響應式設計、Material Design
7. **效能優化**: 程式碼分割、懶載入、虛擬滾動
8. **安全性**: 認證授權、XSS 防護、CSRF 防護
9. **可訪問性**: 符合 WCAG 2.1 AA 標準
10. **測試策略**: 單元測試、組件測試、E2E 測試

此設計確保系統具有良好的可維護性、可擴展性和使用者體驗。
