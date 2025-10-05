from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    BigInteger,
    Integer,
)
from sqlalchemy.orm import relationship

from app.config import settings
from app.models.base import Base, Auditable


class ApprovalTemplateStep(Base, Auditable):
    __tablename__ = "approval_template_steps"
    __table_args__ = {"schema": settings.db_schema, "extend_existing": True}

    id = Column(BigInteger, primary_key=True)
    approval_template_id = Column(
        BigInteger,
        ForeignKey(
            f"{settings.db_schema}.approval_templates.id" if settings.db_schema else "approval_templates.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    step_order = Column(Integer, nullable=False)
    role_id = Column(BigInteger)
    user_id = Column(BigInteger)
    is_deleted = Column(Boolean, nullable=False, default=False)

    approval_template = relationship("ApprovalTemplate", back_populates="steps")