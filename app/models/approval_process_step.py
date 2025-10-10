from sqlalchemy import (
    BigInteger,
    Boolean,  # Added
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
from app.models.enums import ApprovalProcessStepStatus, ApprovalStepType  # Added


class ApprovalProcessStep(Base):
    __tablename__ = "approval_process_steps"
    __table_args__ = {"schema": settings.db_schema}

    id = Column(BigInteger, primary_key=True)
    approval_process_id = Column(BigInteger, ForeignKey(f"{settings.db_schema}.approval_processes.id", ondelete="CASCADE"))
    step_order = Column(Integer, nullable=False)
    approval_type = Column(Enum(ApprovalStepType, name="approval_step_type", schema=settings.db_schema), nullable=False)  # Added

    # This status is the aggregate status of the step, determined by the approvers' statuses and the approval_type
    status = Column(
        Enum(ApprovalProcessStepStatus, name="approval_process_step_status", schema=settings.db_schema),
        nullable=False,
        default=ApprovalProcessStepStatus.PENDING,
    )

    # Removed approver_id, proxy_id, action_at, comment

    created_by = Column(BigInteger)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_by = Column(BigInteger)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, nullable=False, default=False) # Replaced soft delete

    approval_process = relationship("ApprovalProcess", back_populates="steps")
    approvers = relationship("ApprovalProcessStepApprover", back_populates="approval_process_step")  # Added