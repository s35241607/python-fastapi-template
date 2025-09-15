from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.ticket import TicketStatus

# User schemas
class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Comment schemas
class CommentBase(BaseModel):
    content: str
    user_id: int

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    ticket_id: int
    created_at: datetime
    user: Optional[User] = None

    model_config = ConfigDict(from_attributes=True)

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
    comments: List[Comment] = []

    model_config = ConfigDict(from_attributes=True)

# Complex schemas for operations
class TicketWithInitialComment(BaseModel):
    ticket: TicketCreate
    initial_comment: CommentCreate
