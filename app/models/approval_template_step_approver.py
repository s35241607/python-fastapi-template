from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from app.config import settings
from app.models.base import Base


class ApprovalTemplateStepApprover(Base):
    __tablename__ = "approval_template_step_approvers"
    __table_args__ = (
        UniqueConstraint("approval_template_step_id", "role_id", "user_id"),
        {"schema": settings.db_schema},
    )

    id = Column(BigInteger, primary_key=True)
    approval_template_step_id = Column(
        BigInteger, ForeignKey(f"{settings.db_schema}.approval_template_steps.id", ondelete="CASCADE"), nullable=False
    )
    role_id = Column(BigInteger)
    user_id = Column(BigInteger)
    created_by = Column(BigInteger)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_by = Column(BigInteger)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to the parent step
    approval_template_step = relationship("ApprovalTemplateStep", back_populates="approvers")
