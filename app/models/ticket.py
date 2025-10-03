from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Enum,
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
from app.models.enums import TicketPriority, TicketStatus, TicketVisibility

ticket_categories = Table(
    "ticket_categories",
    Base.metadata,
    Column("ticket_id", Integer, ForeignKey(f"{settings.db_schema}.tickets.id" if settings.db_schema else "tickets.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", Integer, ForeignKey(f"{settings.db_schema}.categories.id" if settings.db_schema else "categories.id", ondelete="CASCADE"), primary_key=True),
    schema=settings.db_schema,
)

ticket_labels = Table(
    "ticket_labels",
    Base.metadata,
    Column("ticket_id", Integer, ForeignKey(f"{settings.db_schema}.tickets.id" if settings.db_schema else "tickets.id", ondelete="CASCADE"), primary_key=True),
    Column("label_id", Integer, ForeignKey(f"{settings.db_schema}.labels.id" if settings.db_schema else "labels.id", ondelete="CASCADE"), primary_key=True),
    schema=settings.db_schema,
)


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = {"schema": settings.db_schema}

    id = Column(Integer, primary_key=True)
    ticket_no = Column(String(50), nullable=False, unique=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    ticket_template_id = Column(Integer, ForeignKey(f"{settings.db_schema}.ticket_templates.id" if settings.db_schema else "ticket_templates.id", ondelete="SET NULL"))
    approval_template_id = Column(Integer, ForeignKey(f"{settings.db_schema}.approval_templates.id" if settings.db_schema else "approval_templates.id", ondelete="SET NULL"))
    custom_fields_data = Column(JSON)
    status = Column(
        Enum(TicketStatus, name="ticket_status", schema=settings.db_schema), nullable=False, default=TicketStatus.DRAFT
    )
    priority = Column(Enum(TicketPriority, name="ticket_priority", schema=settings.db_schema), default=TicketPriority.MEDIUM)
    visibility = Column(
        Enum(TicketVisibility, name="ticket_visibility", schema=settings.db_schema),
        nullable=False,
        default=TicketVisibility.INTERNAL,
    )
    due_date = Column(DateTime(timezone=True))
    created_by = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_by = Column(Integer)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_by = Column(Integer)
    deleted_at = Column(DateTime(timezone=True))
    assigned_to = Column(Integer)

    categories = relationship("Category", secondary=ticket_categories, back_populates="tickets")
    labels = relationship("Label", secondary=ticket_labels, back_populates="tickets")
    ticket_template = relationship("TicketTemplate", back_populates="tickets")
    approval_template = relationship("ApprovalTemplate")
    attachments = relationship("TicketAttachment", back_populates="ticket")
    view_permissions = relationship("TicketViewPermission", back_populates="ticket")
    notes = relationship("TicketNote", back_populates="ticket", cascade="all, delete-orphan")
    approval_process = relationship("ApprovalProcess", uselist=False, back_populates="ticket", cascade="all, delete-orphan")
