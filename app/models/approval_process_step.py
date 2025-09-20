from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.config import settings
from app.models.base import Base
from app.models.enums import ApprovalProcessStepStatus


class ApprovalProcessStep(Base):
    __tablename__ = "approval_process_steps"
    __table_args__ = {"schema": settings.db_schema}

    id = Column(BigInteger, primary_key=True)
    approval_process_id = Column(BigInteger, ForeignKey("ticket.approval_processes.id", ondelete="CASCADE"))
    step_order = Column(Integer, nullable=False)
    approver_id = Column(BigInteger)
    proxy_id = Column(BigInteger)
    status = Column(
        Enum(ApprovalProcessStepStatus, name="approval_process_step_status", schema=settings.db_schema),
        nullable=False,
        default=ApprovalProcessStepStatus.PENDING,
    )
    action_at = Column(DateTime(timezone=True))
    comment = Column(Text)
    created_by = Column(BigInteger)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_by = Column(BigInteger)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_by = Column(BigInteger)
    deleted_at = Column(DateTime(timezone=True))

    approval_process = relationship("ApprovalProcess", back_populates="steps")
