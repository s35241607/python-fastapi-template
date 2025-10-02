from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    func,
)
from sqlalchemy.orm import relationship

from app.config import settings
from app.models.base import Base
from app.models.enums import ApprovalProcessStatus


class ApprovalProcess(Base):
    __tablename__ = "approval_processes"
    __table_args__ = {"schema": settings.db_schema, "extend_existing": True}

    id = Column(BigInteger, primary_key=True)
    ticket_id = Column(BigInteger, ForeignKey(f"{settings.db_schema}.tickets.id", ondelete="CASCADE"), unique=True)
    approval_template_id = Column(
        BigInteger, ForeignKey(f"{settings.db_schema}.approval_templates.id", ondelete="SET NULL")
    )
    status = Column(
        Enum(ApprovalProcessStatus, name="approval_process_status", schema=settings.db_schema), nullable=False
    )
    current_step = Column(Integer, default=1)
    created_by = Column(BigInteger)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_by = Column(BigInteger)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_by = Column(BigInteger)
    deleted_at = Column(DateTime(timezone=True))

    ticket = relationship("Ticket", back_populates="approval_process")
    steps = relationship("ApprovalProcessStep", back_populates="approval_process", cascade="all, delete-orphan")
    approval_template = relationship("ApprovalTemplate")