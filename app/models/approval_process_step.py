from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    BigInteger,
    Integer,
    Text,
)
from sqlalchemy.orm import relationship

from app.config import settings
from app.models.base import Base, Auditable
from app.models.enums import ApprovalProcessStepStatus


class ApprovalProcessStep(Base, Auditable):
    __tablename__ = "approval_process_steps"
    __table_args__ = {"schema": settings.db_schema, "extend_existing": True}

    id = Column(BigInteger, primary_key=True)
    approval_process_id = Column(
        BigInteger,
        ForeignKey(
            f"{settings.db_schema}.approval_processes.id" if settings.db_schema else "approval_processes.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
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
    is_deleted = Column(Boolean, nullable=False, default=False)

    approval_process = relationship("ApprovalProcess", back_populates="steps")