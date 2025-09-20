from sqlalchemy import (
    Column,
    BigInteger,
    String,
    DateTime,
    func,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.config import settings


class TicketNoteAttachment(Base):
    __tablename__ = "ticket_note_attachments"
    __table_args__ = {"schema": settings.db_schema}

    id = Column(BigInteger, primary_key=True)
    note_id = Column(BigInteger, ForeignKey("ticket.ticket_notes.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String(100), nullable=False)
    created_by = Column(BigInteger)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    note = relationship("TicketNote", back_populates="attachments")
