from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
from app.config import settings

class Comment(Base):
    __tablename__ = "comments"
    __table_args__ = {"schema": settings.schema}

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    ticket_id = Column(Integer, ForeignKey(f"{settings.schema}.tickets.id"), nullable=False)
    user_id = Column(Integer, ForeignKey(f"{settings.schema}.users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 關聯
    ticket = relationship("Ticket", back_populates="comments")
    user = relationship("User", back_populates="comments")
