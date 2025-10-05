from sqlalchemy import (
    Boolean,
    Column,
    BigInteger,
    String,
)
from sqlalchemy.orm import relationship

from app.config import settings
from app.models.base import Base, Auditable


class ApprovalTemplate(Base, Auditable):
    __tablename__ = "approval_templates"
    __table_args__ = {"schema": settings.db_schema, "extend_existing": True}

    id = Column(BigInteger, primary_key=True)
    name = Column(String(200), nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)

    steps = relationship("ApprovalTemplateStep", back_populates="approval_template", cascade="all, delete-orphan")
    ticket_templates = relationship("TicketTemplate", back_populates="approval_template")