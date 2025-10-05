from sqlalchemy import (
    Boolean,
    Column,
    Enum,
    ForeignKey,
    BigInteger,
    Integer,
)
from sqlalchemy.orm import relationship

from app.config import settings
from app.models.base import Base, Auditable
from app.models.enums import ApprovalProcessStatus


class ApprovalProcess(Base, Auditable):
    __tablename__ = "approval_processes"
    __table_args__ = {"schema": settings.db_schema, "extend_existing": True}

    id = Column(BigInteger, primary_key=True)
    ticket_id = Column(
        BigInteger,
        ForeignKey(f"{settings.db_schema}.tickets.id" if settings.db_schema else "tickets.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    approval_template_id = Column(
        BigInteger,
        ForeignKey(
            f"{settings.db_schema}.approval_templates.id" if settings.db_schema else "approval_templates.id",
            ondelete="SET NULL",
        ),
    )
    status = Column(
        Enum(ApprovalProcessStatus, name="approval_process_status", schema=settings.db_schema), nullable=False
    )
    current_step = Column(Integer, default=1)
    is_deleted = Column(Boolean, nullable=False, default=False)

    ticket = relationship("Ticket", back_populates="approval_process")
    steps = relationship("ApprovalProcessStep", back_populates="approval_process", cascade="all, delete-orphan")
    approval_template = relationship("ApprovalTemplate")