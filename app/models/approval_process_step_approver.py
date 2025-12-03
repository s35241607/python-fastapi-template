from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.config import settings
from app.models.base import Base
from app.models.enums import ApprovalProcessStepStatus


class ApprovalProcessStepApprover(Base):
    __tablename__ = "approval_process_step_approvers"
    __table_args__ = {"schema": settings.DB_SCHEMA}

    id = Column(BigInteger, primary_key=True)
    approval_process_step_id = Column(
        BigInteger, ForeignKey(f"{settings.DB_SCHEMA}.approval_process_steps.id", ondelete="CASCADE"), nullable=False
    )

    # Who is assigned?
    user_id = Column(BigInteger)
    role_id = Column(BigInteger)

    # Who took the action?
    actioned_by_id = Column(BigInteger)
    delegated_for_id = Column(BigInteger)

    # What was the result?
    status = Column(
        Enum(ApprovalProcessStepStatus, name="approval_process_step_status", schema=settings.DB_SCHEMA),
        nullable=False,
        default=ApprovalProcessStepStatus.PENDING,
    )
    action_at = Column(DateTime(timezone=True))
    comment = Column(Text)

    # Audit fields
    created_by = Column(BigInteger)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_by = Column(BigInteger)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to the parent step
    approval_process_step = relationship("ApprovalProcessStep", back_populates="approvers")
