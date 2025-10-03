from sqlalchemy import (
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
    __table_args__ = {"schema": settings.db_schema, "extend_existing": True}

    id = Column(Integer, primary_key=True)
    approval_process_id = Column(
    Integer,
    ForeignKey(
        f"{settings.db_schema}.approval_processes.id" if settings.db_schema else "approval_processes.id",
        ondelete="CASCADE",
    ),
    )
    step_order = Column(Integer, nullable=False)
    approver_id = Column(Integer)
    proxy_id = Column(Integer)
    status = Column(
        Enum(ApprovalProcessStepStatus, name="approval_process_step_status", schema=settings.db_schema),
        nullable=False,
        default=ApprovalProcessStepStatus.PENDING,
    )
    action_at = Column(DateTime(timezone=True))
    comment = Column(Text)
    created_by = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_by = Column(Integer)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_by = Column(Integer)
    deleted_at = Column(DateTime(timezone=True))

    approval_process = relationship("ApprovalProcess", back_populates="steps")