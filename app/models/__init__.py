# Import all models to ensure they are registered with SQLAlchemy
from app.models.base import Base
from app.models.user import User
from app.models.ticket import Ticket, TicketStatus
from app.models.comment import Comment

__all__ = ["Base", "User", "Ticket", "TicketStatus", "Comment"]