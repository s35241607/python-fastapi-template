from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.config import settings
from app.models.base import Base
from app.config import settings

ticket_template_categories = Table(
    "ticket_template_categories",
    Base.metadata,
    Column("ticket_template_id", Integer, ForeignKey(f"{settings.db_schema}.ticket_templates.id" if settings.db_schema else "ticket_templates.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", Integer, ForeignKey(f"{settings.db_schema}.categories.id" if settings.db_schema else "categories.id", ondelete="CASCADE"), primary_key=True),
    schema=settings.db_schema,
)

ticket_template_labels = Table(
    "ticket_template_labels",
    Base.metadata,
    Column("ticket_template_id", Integer, ForeignKey(f"{settings.db_schema}.ticket_templates.id" if settings.db_schema else "ticket_templates.id", ondelete="CASCADE"), primary_key=True),
    Column("label_id", Integer, ForeignKey(f"{settings.db_schema}.labels.id" if settings.db_schema else "labels.id", ondelete="CASCADE"), primary_key=True),
    schema=settings.db_schema,
)


class TicketTemplate(Base):
    __tablename__ = "ticket_templates"
    __table_args__ = {"schema": settings.db_schema}

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    custom_fields_schema = Column(JSON)
    approval_template_id = Column(Integer, ForeignKey(f"{settings.db_schema}.approval_templates.id" if settings.db_schema else "approval_templates.id"))
    created_by = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_by = Column(Integer)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_by = Column(Integer)
    deleted_at = Column(DateTime(timezone=True))

    categories = relationship("Category", secondary=ticket_template_categories, back_populates="ticket_templates")
    labels = relationship("Label", secondary=ticket_template_labels, back_populates="ticket_templates")
    approval_template = relationship("ApprovalTemplate", back_populates="ticket_templates")
    tickets = relationship("Ticket", back_populates="ticket_template")
