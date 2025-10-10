from sqlalchemy import (
    BigInteger,
    Boolean,  # Added
    Column,
    DateTime,
    String,
    func,
)
from sqlalchemy.orm import relationship

from app.config import settings
from app.models.base import Base


class ApprovalTemplate(Base):
    __tablename__ = "approval_templates"
    __table_args__ = {"schema": settings.db_schema}

    id = Column(BigInteger, primary_key=True)
    name = Column(String(200), nullable=False)
    created_by = Column(BigInteger)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_by = Column(BigInteger)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, nullable=False, default=False)  # Replaced soft delete columns

    steps = relationship("ApprovalTemplateStep", back_populates="approval_template")
    ticket_templates = relationship("TicketTemplate", back_populates="approval_template")