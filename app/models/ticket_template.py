from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,  # Added
    Column,
    DateTime,
    ForeignKey,
    String,
    Table,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.config import settings
from app.models.base import Base

ticket_template_categories = Table(
    "ticket_template_categories",
    Base.metadata,
    Column(
        "ticket_template_id",
        BigInteger,
        ForeignKey(f"{settings.DB_SCHEMA}.ticket_templates.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("category_id", BigInteger, ForeignKey(f"{settings.DB_SCHEMA}.categories.id", ondelete="CASCADE"), primary_key=True),
    schema=settings.DB_SCHEMA,
)

ticket_template_labels = Table(
    "ticket_template_labels",
    Base.metadata,
    Column(
        "ticket_template_id",
        BigInteger,
        ForeignKey(f"{settings.DB_SCHEMA}.ticket_templates.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("label_id", BigInteger, ForeignKey(f"{settings.DB_SCHEMA}.labels.id", ondelete="CASCADE"), primary_key=True),
    schema=settings.DB_SCHEMA,
)


class TicketTemplate(Base):
    __tablename__ = "ticket_templates"
    __table_args__ = {"schema": settings.DB_SCHEMA}

    id = Column(BigInteger, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    custom_fields_schema = Column(JSON)
    approval_template_id = Column(BigInteger, ForeignKey(f"{settings.DB_SCHEMA}.approval_templates.id"))
    created_by = Column(BigInteger)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_by = Column(BigInteger)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, nullable=False, default=False)  # Replaced soft delete columns

    categories = relationship("Category", secondary=ticket_template_categories, back_populates="ticket_templates")
    labels = relationship("Label", secondary=ticket_template_labels, back_populates="ticket_templates")
    approval_template = relationship("ApprovalTemplate", back_populates="ticket_templates")
    tickets = relationship("Ticket", back_populates="ticket_template")
