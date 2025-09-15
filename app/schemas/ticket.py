from pydantic import BaseModel, ConfigDict
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from app.models.ticket import TicketStatus
from app.schemas.user import User

if TYPE_CHECKING:
    from app.schemas.comment import Comment, CommentCreate

# Ticket schemas
class TicketBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[TicketStatus] = TicketStatus.OPEN
    user_id: int

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TicketStatus] = None

class Ticket(TicketBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    user: Optional[User] = None
    comments: List["Comment"] = []

    model_config = ConfigDict(from_attributes=True)

# Complex schemas for operations
class TicketWithInitialComment(BaseModel):
    ticket: TicketCreate
    initial_comment: "CommentCreate"
