from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    BigInteger,
    Text,
    and_,
)
from sqlalchemy.orm import relationship

from app.config import settings
from app.models.base import Base, Auditable
from app.models.enums import TicketEventType


class TicketNote(Base, Auditable):
    __tablename__ = "ticket_notes"
    __table_args__ = {"schema": settings.db_schema, "extend_existing": True}

    id = Column(BigInteger, primary_key=True)
    ticket_id = Column(
        BigInteger,
        ForeignKey(f"{settings.db_schema}.tickets.id" if settings.db_schema else "tickets.id", ondelete="CASCADE"),
        nullable=False,
    )
    author_id = Column(BigInteger, nullable=False)
    note = Column(Text)
    system = Column(Boolean, nullable=False)
    event_type = Column(Enum(TicketEventType, name="ticket_event_type", schema=settings.db_schema))
    event_details = Column(JSON)
    is_deleted = Column(Boolean, nullable=False, default=False)

    ticket = relationship("Ticket", back_populates="notes")

    attachments = relationship(
        "Attachment",
        primaryjoin="and_(TicketNote.id == Attachment.related_id, Attachment.related_type == 'note')",
        cascade="all, delete-orphan",
        lazy="selectin",
    )