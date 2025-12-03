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
    __table_args__ = {"schema": settings.DB_SCHEMA}

    id = Column(BigInteger, primary_key=True)
    ticket_id = Column(BigInteger, ForeignKey(f"{settings.DB_SCHEMA}.tickets.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(BigInteger, nullable=False)
    note = Column(Text)
    system = Column(Boolean, nullable=False)
    event_type = Column(Enum(TicketEventType, name="ticket_event_type", schema=settings.DB_SCHEMA))
    event_details = Column(JSON)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, onupdate=func.now())
    is_deleted = Column(Boolean, nullable=False, default=False)  # Replaced soft delete columns

    ticket = relationship("Ticket", back_populates="notes")
