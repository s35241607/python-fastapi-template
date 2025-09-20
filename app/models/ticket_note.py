from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.config import settings
from app.models.base import Base
from app.models.enums import TicketEventType


class TicketNote(Base):
    __tablename__ = "ticket_notes"
    __table_args__ = {"schema": settings.db_schema}

    id = Column(BigInteger, primary_key=True)
    ticket_id = Column(BigInteger, ForeignKey("ticket.tickets.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(BigInteger, nullable=False)
    note = Column(Text)
    system = Column(Boolean, nullable=False)
    event_type = Column(Enum(TicketEventType, name="ticket_event_type", schema=settings.db_schema))
    event_details = Column(JSON)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, onupdate=func.now())
    deleted_by = Column(BigInteger)
    deleted_at = Column(DateTime(timezone=True))

    ticket = relationship("Ticket", back_populates="notes")
    attachments = relationship("TicketNoteAttachment", back_populates="note")
