from sqlalchemy import (
    Column,
    BigInteger,
    String,
    DateTime,
    func,
)
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.config import settings


class ApprovalTemplate(Base):
    __tablename__ = "approval_templates"
    __table_args__ = {"schema": settings.db_schema}

    id = Column(BigInteger, primary_key=True)
    name = Column(String(200), nullable=False)
    created_by = Column(BigInteger)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_by = Column(BigInteger)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_by = Column(BigInteger)
    deleted_at = Column(DateTime(timezone=True))

    steps = relationship("ApprovalTemplateStep", back_populates="approval_template")
    ticket_templates = relationship("TicketTemplate", back_populates="approval_template")
