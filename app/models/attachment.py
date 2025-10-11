from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Enum,
    String,
    Text,
    func,
)

from app.config import settings
from app.models.base import Base
from app.models.enums import AttachmentUsageType


class Attachment(Base):
    __tablename__ = "attachments"
    __table_args__ = {"schema": settings.db_schema}

    id = Column(BigInteger, primary_key=True)
    related_type = Column(String(50), nullable=True)  # e.g., 'tickets', 'ticket_notes' - nullable for pre-upload
    related_id = Column(BigInteger, nullable=True)
    ticket_id = Column(BigInteger)  # For quick lookup
    usage_type = Column(
        Enum(AttachmentUsageType, name="attachment_usage_type", schema=settings.db_schema),
        nullable=False,
        default=AttachmentUsageType.GENERAL,
    )
    file_name = Column(String(255), nullable=False)
    storage_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String(100), nullable=False)
    storage_provider = Column(String(50), default="local")
    description = Column(Text)
    created_by = Column(BigInteger)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_by = Column(BigInteger)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, nullable=False, default=False)
