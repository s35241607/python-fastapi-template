import enum


class TicketStatus(str, enum.Enum):
    DRAFT = "draft"
    WAITING_APPROVAL = "waiting_approval"
    REJECTED = "rejected"
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ApprovalProcessStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ApprovalProcessStepStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class TicketEventType(str, enum.Enum):
    STATE_CHANGE = "state_change"
    TITLE_CHANGE = "title_change"
    DESCRIPTION_CHANGE = "description_change"
    STATUS_CHANGE = "status_change"
    PRIORITY_CHANGE = "priority_change"
    ASSIGNED_TO_CHANGE = "assigned_to_change"
    DUE_DATE_CHANGE = "due_date_change"
    ATTACHMENT_ADD = "attachment_add"
    ATTACHMENT_REMOVE = "attachment_remove"
    APPROVAL_SUBMITTED = "approval_submitted"
    APPROVAL_APPROVED = "approval_approved"
    APPROVAL_REJECTED = "approval_rejected"
    LABEL_ADD = "label_add"
    LABEL_REMOVE = "label_remove"


class NotificationEvent(str, enum.Enum):
    ON_CREATE = "on_create"
    ON_CLOSE = "on_close"
    ON_STATUS_CHANGE = "on_status_change"
    ON_NEW_COMMENT = "on_new_comment"


class TicketVisibility(str, enum.Enum):
    INTERNAL = "internal"
    RESTRICTED = "restricted"


class AttachmentUsageType(str, enum.Enum):
    GENERAL = "general"
    INLINE = "inline"
