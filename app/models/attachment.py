from sqlalchemy import BigInteger, Column, String, Enum
from sqlalchemy.orm import relationship

from app.config import settings
from app.models.base import Base, Auditable
from app.models.enums import AttachmentUsageType


class Attachment(Base, Auditable):
    __tablename__ = "attachments"
    __table_args__ = {"schema": settings.db_schema, "extend_existing": True}

    id = Column(BigInteger, primary_key=True, index=True)

    # Polymorphic association fields
    related_type = Column(String(50), nullable=False)  # e.g., 'ticket', 'note'
    related_id = Column(BigInteger, nullable=False)

    ticket_id = Column(BigInteger) # For quick lookups

    usage_type = Column(Enum(AttachmentUsageType), nullable=False, default=AttachmentUsageType.GENERAL)

    file_name = Column(String(255), nullable=False)
    storage_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String(100), nullable=False)
    storage_provider = Column(String(50), default="local")
    description = Column(String)

    __mapper_args__ = {
        "polymorphic_on": related_type,
        "polymorphic_identity": "attachment"
    }