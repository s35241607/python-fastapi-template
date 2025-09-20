# Import all models to ensure they are registered with SQLAlchemy
from app.models.approval_process import ApprovalProcess
from app.models.approval_process_step import ApprovalProcessStep
from app.models.approval_template import ApprovalTemplate
from app.models.approval_template_step import ApprovalTemplateStep
from app.models.base import Base
from app.models.category import Category
from app.models.enums import (
    ApprovalProcessStatus,
    ApprovalProcessStepStatus,
    NotificationEvent,
    TicketEventType,
    TicketPriority,
    TicketStatus,
    TicketVisibility,
)
from app.models.label import Label
from app.models.notification_rule import NotificationRule
from app.models.ticket import Ticket
from app.models.ticket_attachment import TicketAttachment
from app.models.ticket_note import TicketNote
from app.models.ticket_note_attachment import TicketNoteAttachment
from app.models.ticket_template import TicketTemplate
from app.models.ticket_view_permission import TicketViewPermission

__all__ = [
    "Base",
    "Ticket",
    "Category",
    "Label",
    "TicketAttachment",
    "TicketNote",
    "TicketNoteAttachment",
    "TicketTemplate",
    "TicketViewPermission",
    "ApprovalProcess",
    "ApprovalProcessStep",
    "ApprovalTemplate",
    "ApprovalTemplateStep",
    "NotificationRule",
    "TicketStatus",
    "TicketPriority",
    "ApprovalProcessStatus",
    "ApprovalProcessStepStatus",
    "TicketEventType",
    "NotificationEvent",
    "TicketVisibility",
]
