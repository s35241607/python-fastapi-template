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


class TicketAttachment(Base):
    __tablename__ = "ticket_attachments"
    __table_args__ = {"schema": settings.db_schema}

    id = Column(Integer, primary_key=True)
    ticket_id = Column(
        Integer,
        ForeignKey(f"{settings.db_schema}.tickets.id" if settings.db_schema else "tickets.id", ondelete="CASCADE"),
    )
    file_name = Column(String(255))
    file_path = Column(String(500))
    file_size = Column(Integer)
    mime_type = Column(String(100))
    created_by = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_by = Column(Integer)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_by = Column(Integer)
    deleted_at = Column(DateTime(timezone=True))

    ticket = relationship("Ticket", back_populates="attachments")
