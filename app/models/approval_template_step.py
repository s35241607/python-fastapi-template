from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Enum,  # Added
    ForeignKey,
    Integer,
    func,
)
from sqlalchemy.orm import relationship

from app.config import settings  # Added
from app.models.base import Base
from app.models.enums import ApprovalStepType  # Added


class ApprovalTemplateStep(Base):
    __tablename__ = "approval_template_steps"
    __table_args__ = {"schema": settings.db_schema}  # Updated schema

    id = Column(BigInteger, primary_key=True)
    approval_template_id = Column(BigInteger, ForeignKey(f"{settings.db_schema}.approval_templates.id", ondelete="CASCADE"))
    step_order = Column(Integer, nullable=False)
    approval_type = Column(Enum(ApprovalStepType, name="approval_step_type", schema=settings.db_schema), nullable=False)  # Added

    # Removed role_id, user_id, is_mandatory

    created_by = Column(BigInteger)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_by = Column(BigInteger)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, nullable=False, default=False) # Replaced soft delete

    approval_template = relationship("ApprovalTemplate", back_populates="steps")
    approvers = relationship("ApprovalTemplateStepApprover", back_populates="approval_template_step")  # Added