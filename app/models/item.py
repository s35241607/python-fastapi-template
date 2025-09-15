from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
import enum

class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "ticket"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 關聯
    tickets = relationship("Ticket", back_populates="user")
    comments = relationship("Comment", back_populates="user")

class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = {"schema": "ticket"}

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(Enum(TicketStatus), default=TicketStatus.OPEN)
    user_id = Column(Integer, ForeignKey("ticket.users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 關聯
    user = relationship("User", back_populates="tickets")
    comments = relationship("Comment", back_populates="ticket", cascade="all, delete-orphan")

class Comment(Base):
    __tablename__ = "comments"
    __table_args__ = {"schema": "ticket"}

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    ticket_id = Column(Integer, ForeignKey("ticket.tickets.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("ticket.users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 關聯
    ticket = relationship("Ticket", back_populates="comments")
    user = relationship("User", back_populates="comments")
