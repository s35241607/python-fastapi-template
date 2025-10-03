from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    func,
)
from sqlalchemy.orm import relationship

from app.config import settings
from app.models.base import Base


class ApprovalTemplateStep(Base):
    __tablename__ = "approval_template_steps"
    __table_args__ = {"schema": settings.db_schema, "extend_existing": True}

    id = Column(Integer, primary_key=True)
    approval_template_id = Column(
        Integer,
    ForeignKey(
        f"{settings.db_schema}.approval_templates.id" if settings.db_schema else "approval_templates.id",
        ondelete="CASCADE",
    ),
    )
    step_order = Column(Integer, nullable=False)
    role_id = Column(Integer)
    user_id = Column(Integer)
    is_mandatory = Column(Boolean, default=True)
    created_by = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_by = Column(Integer)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_by = Column(Integer)
    deleted_at = Column(DateTime(timezone=True))

    approval_template = relationship("ApprovalTemplate", back_populates="steps")