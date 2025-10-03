from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship

from app.config import settings
from app.models.base import Base


class TicketNoteAttachment(Base):
    __tablename__ = "ticket_note_attachments"
    __table_args__ = {"schema": settings.db_schema, "extend_existing": True}

    id = Column(Integer, primary_key=True)
    note_id = Column(
        Integer,
        ForeignKey(f"{settings.db_schema}.ticket_notes.id" if settings.db_schema else "ticket_notes.id", ondelete="CASCADE"),
        nullable=False,
    )
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    created_by = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    note = relationship("TicketNote", back_populates="attachments")