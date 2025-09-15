from pydantic import BaseModel, ConfigDict
from typing import Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.schemas.user import User

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
    user: Optional["User"] = None

    model_config = ConfigDict(from_attributes=True)
