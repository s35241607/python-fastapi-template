from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship

from app.config import settings
from app.models.base import Base


class ApprovalTemplate(Base):
    __tablename__ = "approval_templates"
    __table_args__ = {"schema": settings.db_schema, "extend_existing": True}

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    created_by = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_by = Column(Integer)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_by = Column(Integer)
    deleted_at = Column(DateTime(timezone=True))

    steps = relationship("ApprovalTemplateStep", back_populates="approval_template", cascade="all, delete-orphan")
    ticket_templates = relationship("TicketTemplate", back_populates="approval_template")