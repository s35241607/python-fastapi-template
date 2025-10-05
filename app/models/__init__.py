# Import all models to ensure they are registered with SQLAlchemy
from .approval_process import ApprovalProcess
from .approval_process_step import ApprovalProcessStep
from .approval_template import ApprovalTemplate
from .approval_template_step import ApprovalTemplateStep
from .attachment import Attachment
from .base import Base, Auditable
from .category import Category
from .enums import (
    ApprovalProcessStatus,
    ApprovalProcessStepStatus,
    AttachmentUsageType,
    NotificationEvent,
    TicketEventType,
    TicketPriority,
    TicketStatus,
    TicketVisibility,
)
from .label import Label
from .notification_rule import NotificationRule, NotificationRuleRole, NotificationRuleUser
from .ticket import Ticket
from .ticket_note import TicketNote
from .ticket_template import TicketTemplate
from .ticket_view_permission import TicketViewPermission

__all__ = [
    "Base",
    "Auditable",
    "Ticket",
    "Category",
    "Label",
    "Attachment",
    "TicketNote",
    "TicketTemplate",
    "TicketViewPermission",
    "ApprovalProcess",
    "ApprovalProcessStep",
    "ApprovalTemplate",
    "ApprovalTemplateStep",
    "NotificationRule",
    "NotificationRuleUser",
    "NotificationRuleRole",
    # Enums
    "TicketStatus",
    "TicketPriority",
    "ApprovalProcessStatus",
    "ApprovalProcessStepStatus",
    "TicketEventType",
    "NotificationEvent",
    "TicketVisibility",
    "AttachmentUsageType",
]