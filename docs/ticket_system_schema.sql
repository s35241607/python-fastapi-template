-- ====================================================================
--                   Ticket 系統 Schema
-- ====================================================================
--
-- 此 Schema 結合了詳細的企業功能（工單模板、簽核流程）與
-- GitLab 風格的統一事件流（`ticket_notes`），提供了一個強大且可擴充的基礎。
--

-- =========================================
-- ENUMS
-- =========================================
CREATE TYPE ticket_status AS ENUM (
    'draft', 'waiting_approval', 'rejected', 'open',
    'in_progress', 'resolved', 'closed', 'cancelled'
);

CREATE TYPE ticket_priority AS ENUM (
    'low', 'medium', 'high', 'urgent'
);

CREATE TYPE approval_process_status AS ENUM (
    'pending', 'approved', 'rejected'
);

CREATE TYPE approval_process_step_status AS ENUM (
    'pending', 'approved', 'rejected'
);

CREATE TYPE ticket_event_type AS ENUM (
    'state_change', 'title_change', 'description_change', 'status_change',
    'priority_change', 'assignee_change', 'due_date_change',
    'attachment_add', 'attachment_remove', 'approval_submitted',
    'approval_approved', 'approval_rejected',
    'label_add', 'label_remove'
);

CREATE TYPE notification_event AS ENUM (
    'on_create',
    'on_close',
    'on_status_change',
    'on_new_comment'
);

CREATE TYPE ticket_visibility AS ENUM (
    'internal',   -- 內部公開 (所有登入者可見)
    'restricted'  -- 限制訪問 (僅特定人員/角色可見)
);

CREATE TYPE attachment_usage_type AS ENUM ('inline', 'general');

-- =========================================
-- Categories & Labels (通用分類與標籤)
-- =========================================
CREATE TABLE categories (
    id               BIGSERIAL PRIMARY KEY,
    name             VARCHAR(100) NOT NULL UNIQUE,
    description      TEXT,
    created_by       BIGINT,
    created_at       TIMESTAMPTZ DEFAULT now(),
    updated_by       BIGINT,
    updated_at       TIMESTAMPTZ DEFAULT now(),
    is_deleted       BOOLEAN NOT NULL DEFAULT false
);

CREATE TABLE labels (
    id          BIGSERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,
    color       VARCHAR(7) NOT NULL, -- #RRGGBB
    description TEXT,
    created_by  BIGINT,
    created_at  TIMESTAMPTZ DEFAULT now(),
    updated_by  BIGINT,
    updated_at  TIMESTAMPTZ DEFAULT now(),
    is_deleted  BOOLEAN NOT NULL DEFAULT false
);


-- =========================================
-- TicketTemplate 與其關聯
-- =========================================
CREATE TABLE ticket_templates (
    id                        BIGSERIAL PRIMARY KEY,
    name                      VARCHAR(200) NOT NULL,
    description               TEXT,
    custom_fields_schema      JSONB,
    approval_template_id BIGINT,
    created_by                BIGINT,
    created_at                TIMESTAMPTZ DEFAULT now(),
    updated_by                BIGINT,
    updated_at                TIMESTAMPTZ DEFAULT now(),
    is_deleted  BOOLEAN NOT NULL DEFAULT false
);

CREATE TABLE ticket_template_categories (
    ticket_template_id      BIGINT REFERENCES ticket_templates(id) ON DELETE CASCADE,
    category_id      BIGINT REFERENCES categories(id) ON DELETE CASCADE,
    PRIMARY KEY(ticket_template_id, category_id)
);

CREATE TABLE ticket_template_labels (
    ticket_template_id BIGINT REFERENCES ticket_templates(id) ON DELETE CASCADE,
    label_id    BIGINT REFERENCES labels(id) ON DELETE CASCADE,
    created_by                BIGINT,
    created_at                TIMESTAMPTZ DEFAULT now(),
    updated_by                BIGINT,
    updated_at                TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (ticket_template_id, label_id)
);


-- =========================================
-- Ticket 主表與其關聯
-- =========================================
CREATE SEQUENCE ticket_no_seq START 1;

CREATE TABLE tickets (
    id                   BIGSERIAL PRIMARY KEY,
    ticket_no            VARCHAR(50) NOT NULL UNIQUE,
    title                VARCHAR(200) NOT NULL,
    description          TEXT,
    ticket_template_id   BIGINT REFERENCES ticket_templates(id) ON DELETE SET NULL,
    approval_template_id BIGINT,
    custom_fields_data   JSONB,
    status               ticket_status NOT NULL DEFAULT 'draft',
    priority             ticket_priority DEFAULT 'medium',
    visibility           ticket_visibility NOT NULL DEFAULT 'internal',
    due_date             TIMESTAMPTZ,
    created_by           BIGINT,
    created_at           TIMESTAMPTZ DEFAULT now(),
    updated_by           BIGINT,
    updated_at           TIMESTAMPTZ DEFAULT now(),
    is_deleted           BOOLEAN NOT NULL DEFAULT false,
    assigned_to          BIGINT
);
COMMENT ON COLUMN tickets.approval_template_id IS '此 Ticket 所使用的簽核範本 ID。';
COMMENT ON COLUMN tickets.ticket_template_id IS '此 Ticket 所使用的範本 ID，若為 NULL 則表示為自訂工單。';

CREATE TABLE ticket_categories (
    ticket_id      BIGINT REFERENCES tickets(id) ON DELETE CASCADE,
    category_id    BIGINT REFERENCES categories(id) ON DELETE CASCADE,
    created_by     BIGINT,
    created_at     TIMESTAMPTZ DEFAULT now(),
    updated_by     BIGINT,
    updated_at     TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY(ticket_id, category_id)
);

CREATE TABLE ticket_labels (
    ticket_id    BIGINT REFERENCES tickets(id) ON DELETE CASCADE,
    label_id     BIGINT REFERENCES labels(id) ON DELETE CASCADE,
    created_by   BIGINT,
    created_at   TIMESTAMPTZ DEFAULT now(),
    updated_by   BIGINT,
    updated_at   TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (ticket_id, label_id)
);

-- =========================================
-- 統一附件表 (Attachments)
-- =========================================
CREATE TABLE attachments (
    id BIGSERIAL PRIMARY KEY,

    related_type VARCHAR(50) NOT NULL,   -- 'ticket', 'note', 'template', ...
    related_id BIGINT NOT NULL,          -- 指向不同資源
    ticket_id BIGINT,                    -- 快速查詢

    usage_type attachment_usage_type NOT NULL DEFAULT 'general',

    file_name VARCHAR(255) NOT NULL,
    storage_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    storage_provider VARCHAR(50) DEFAULT 'local',
    description TEXT,

    created_by BIGINT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_by BIGINT,
    updated_at TIMESTAMPTZ DEFAULT now(),
    is_deleted BOOLEAN NOT NULL DEFAULT false
);

CREATE INDEX idx_attachments_related_not_deleted
ON attachments (related_type, related_id)
WHERE is_deleted = false;

CREATE INDEX idx_attachments_ticket_id
ON attachments (ticket_id)
WHERE is_deleted = false;

-- =========================================
-- 權限設定
-- =========================================
CREATE TABLE ticket_view_permissions (
    ticket_id BIGINT NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    user_id   BIGINT,
    role_id   BIGINT,
    created_by     BIGINT,
    created_at     TIMESTAMPTZ DEFAULT now(),
    updated_by     BIGINT,
    updated_at     TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT chk_permission_target CHECK ((user_id IS NOT NULL AND role_id IS NULL) OR (role_id IS NULL AND user_id IS NOT NULL)),
    UNIQUE (ticket_id, user_id, role_id)
);

-- =========================================
-- 統一事件流 (Notes)
-- =========================================
CREATE TABLE ticket_notes (
    id            BIGSERIAL PRIMARY KEY,
    ticket_id     BIGINT NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    author_id     BIGINT NOT NULL,
    note          TEXT,
    system        BOOLEAN NOT NULL,
    event_type    ticket_event_type,
    event_details JSONB,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_deleted    BOOLEAN NOT NULL DEFAULT false,
    CONSTRAINT chk_note_type CHECK (
        (system IS TRUE AND event_type IS NOT NULL AND note IS NULL) OR
        (system IS FALSE AND event_type IS NULL AND note IS NOT NULL)
    )
);

-- =========================================
-- 簽核範本 (Approval Templates)
-- =========================================
CREATE TABLE approval_templates (
    id               BIGSERIAL PRIMARY KEY,
    name             VARCHAR(200) NOT NULL,
    created_by       BIGINT,
    created_at       TIMESTAMPTZ DEFAULT now(),
    updated_by       BIGINT,
    updated_at       TIMESTAMPTZ DEFAULT now(),
    is_deleted       BOOLEAN NOT NULL DEFAULT false
);
COMMENT ON TABLE approval_templates IS '儲存可重複使用的簽核流程範本';

ALTER TABLE ticket_templates ADD CONSTRAINT fk_approval_template_id
FOREIGN KEY (approval_template_id) REFERENCES approval_templates(id) ON DELETE SET NULL;

ALTER TABLE tickets ADD CONSTRAINT fk_approval_template_id
FOREIGN KEY (approval_template_id) REFERENCES approval_templates(id) ON DELETE SET NULL;

CREATE TABLE approval_template_steps (
    id                   BIGSERIAL PRIMARY KEY,
    approval_template_id BIGINT REFERENCES approval_templates(id) ON DELETE CASCADE,
    step_order           INT NOT NULL,
    role_id              BIGINT,
    user_id              BIGINT,
    created_by           BIGINT,
    created_at           TIMESTAMPTZ DEFAULT now(),
    updated_by           BIGINT,
    updated_at           TIMESTAMPTZ DEFAULT now(),
    is_deleted           BOOLEAN NOT NULL DEFAULT false,
    CONSTRAINT chk_approver_type CHECK ((role_id IS NOT NULL AND user_id IS NULL) OR (role_id IS NULL AND user_id IS NOT NULL))
);
COMMENT ON TABLE approval_template_steps IS '定義簽核範本中的每一個步驟';

-- =========================================
-- 簽核流程實例 (Approval Processes)
-- =========================================
CREATE TABLE approval_processes (
    id                   BIGSERIAL PRIMARY KEY,
    ticket_id            BIGINT REFERENCES tickets(id) ON DELETE CASCADE UNIQUE,
    approval_template_id BIGINT REFERENCES approval_templates(id) ON DELETE SET NULL,
    status               approval_process_status NOT NULL,
    current_step         INT DEFAULT 1,
    created_by           BIGINT,
    created_at           TIMESTAMPTZ DEFAULT now(),
    updated_by           BIGINT,
    updated_at           TIMESTAMPTZ DEFAULT now(),
    is_deleted           BOOLEAN NOT NULL DEFAULT false
);
COMMENT ON TABLE approval_processes IS '一個具體的、正在運行或已完成的簽核流程實例';

CREATE TABLE approval_process_steps (
    id                  BIGSERIAL PRIMARY KEY,
    approval_process_id BIGINT REFERENCES approval_processes(id) ON DELETE CASCADE,
    step_order          INT NOT NULL,
    approver_id         BIGINT,
    proxy_id            BIGINT,
    status              approval_process_step_status NOT NULL DEFAULT 'pending',
    action_at           TIMESTAMPTZ,
    comment             TEXT,
    created_by          BIGINT,
    created_at          TIMESTAMPTZ DEFAULT now(),
    updated_by          BIGINT,
    updated_at          TIMESTAMPTZ DEFAULT now(),
    is_deleted          BOOLEAN NOT NULL DEFAULT false
);
COMMENT ON TABLE approval_process_steps IS '一個具體簽核流程中的每一個步驟的狀態';

-- =========================================
-- 通知設定
-- =========================================
CREATE TABLE notification_rules (
    id                 BIGSERIAL PRIMARY KEY,
    ticket_template_id BIGINT REFERENCES ticket_templates(id) ON DELETE CASCADE,
    ticket_id          BIGINT REFERENCES tickets(id) ON DELETE CASCADE,
    notify_on_event    notification_event NOT NULL,
    created_by         BIGINT,
    created_at         TIMESTAMPTZ DEFAULT now(),
    updated_by         BIGINT,
    updated_at         TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT chk_notification_source CHECK (
        (ticket_template_id IS NOT NULL AND ticket_id IS NULL) OR
        (ticket_template_id IS NULL AND ticket_id IS NOT NULL)
    )
);
COMMENT ON COLUMN notification_rules.ticket_template_id IS '此規則所屬的範本 ID (與 ticket_id 擇一)';

CREATE TABLE notification_rule_users (
    rule_id           BIGINT NOT NULL REFERENCES notification_rules(id) ON DELETE CASCADE,
    user_id           BIGINT NOT NULL,
    created_by        BIGINT,
    created_at        TIMESTAMPTZ DEFAULT now(),
    updated_by        BIGINT,
    updated_at        TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (rule_id, user_id)
);

CREATE TABLE notification_rule_roles (
    rule_id           BIGINT NOT NULL REFERENCES notification_rules(id) ON DELETE CASCADE,
    role_id           BIGINT NOT NULL,
    created_by        BIGINT,
    created_at        TIMESTAMPTZ DEFAULT now(),
    updated_by        BIGINT,
    updated_at        TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (rule_id, role_id)
);

-- =========================================
-- 索引 (INDEXES)
-- =========================================
CREATE INDEX idx_ticket_notes_on_ticket_id_and_created_at ON ticket_notes(ticket_id, created_at DESC);
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_assigned_to ON tickets(assigned_to);
CREATE INDEX idx_approval_processes_ticket_id ON approval_processes(ticket_id);
CREATE INDEX idx_approval_process_steps_process_id ON approval_process_steps(approval_process_id);
CREATE INDEX idx_ticket_categories_ticket_id ON ticket_categories(ticket_id);
CREATE INDEX idx_ticket_categories_category_id ON ticket_categories(category_id);
CREATE INDEX idx_notification_rules_ticket_template_id ON notification_rules(ticket_template_id);
CREATE INDEX idx_notification_rules_ticket_id ON notification_rules(ticket_id);
CREATE INDEX idx_tickets_assigned_to_status ON tickets(assigned_to, status) WHERE status NOT IN ('closed', 'cancelled');
CREATE INDEX idx_ticket_view_permissions_ticket_id ON ticket_view_permissions(ticket_id);