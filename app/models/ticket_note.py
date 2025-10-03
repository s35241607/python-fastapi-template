from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.config import settings
from app.models.base import Base
from app.models.enums import TicketEventType


class TicketNote(Base):
    __tablename__ = "ticket_notes"
    __table_args__ = {"schema": settings.db_schema, "extend_existing": True}

    id = Column(Integer, primary_key=True)
    ticket_id = Column(
        Integer,
        ForeignKey(f"{settings.db_schema}.tickets.id" if settings.db_schema else "tickets.id", ondelete="CASCADE"),
        nullable=False,
    )
    author_id = Column(Integer, nullable=False)
    note = Column(Text)
    system = Column(Boolean, nullable=False)
    event_type = Column(Enum(TicketEventType, name="ticket_event_type", schema=settings.db_schema))
    event_details = Column(JSON)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_by = Column(Integer)
    deleted_at = Column(DateTime(timezone=True))

    ticket = relationship("Ticket", back_populates="notes")
    attachments = relationship("TicketNoteAttachment", back_populates="note", cascade="all, delete-orphan")