from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    func,
)
from sqlalchemy.orm import relationship

from app.models.base import Base


class ApprovalTemplateStep(Base):
    __tablename__ = "approval_template_steps"
    __table_args__ = {"schema": "ticket"}

    id = Column(BigInteger, primary_key=True)
    approval_template_id = Column(BigInteger, ForeignKey("ticket.approval_templates.id", ondelete="CASCADE"))
    step_order = Column(Integer, nullable=False)
    role_id = Column(BigInteger)
    user_id = Column(BigInteger)
    is_mandatory = Column(Boolean, default=True)
    created_by = Column(BigInteger)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_by = Column(BigInteger)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_by = Column(BigInteger)
    deleted_at = Column(DateTime(timezone=True))

    approval_template = relationship("ApprovalTemplate", back_populates="steps")
