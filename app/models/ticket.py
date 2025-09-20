from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Text,
    DateTime,
    func,
    JSON,
    ForeignKey,
    Table,
    Enum,
)
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.config import settings
from app.models.enums import TicketStatus, TicketPriority, TicketVisibility

ticket_categories = Table(
    "ticket_categories",
    Base.metadata,
    Column("ticket_id", BigInteger, ForeignKey(f"{settings.db_schema}.tickets.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", BigInteger, ForeignKey(f"{settings.db_schema}.categories.id", ondelete="CASCADE"), primary_key=True),
    schema="ticket",
)

ticket_labels = Table(
    "ticket_labels",
    Base.metadata,
    Column("ticket_id", BigInteger, ForeignKey(f"{settings.db_schema}.tickets.id", ondelete="CASCADE"), primary_key=True),
    Column("label_id", BigInteger, ForeignKey(f"{settings.db_schema}.labels.id", ondelete="CASCADE"), primary_key=True),
    schema="ticket",
)


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = {"schema": settings.db_schema}

    id = Column(BigInteger, primary_key=True)
    ticket_no = Column(String(50), nullable=False, unique=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    ticket_template_id = Column(BigInteger, ForeignKey(f"{settings.db_schema}.ticket_templates.id", ondelete="SET NULL"))
    approval_template_id = Column(BigInteger, ForeignKey(f"{settings.db_schema}.approval_templates.id", ondelete="SET NULL"))
    custom_fields_data = Column(JSON)
    status = Column(Enum(TicketStatus, name="ticket_status", schema=settings.db_schema), nullable=False, default=TicketStatus.DRAFT)
    priority = Column(Enum(TicketPriority, name="ticket_priority", schema=settings.db_schema), default=TicketPriority.MEDIUM)
    visibility = Column(Enum(TicketVisibility, name="ticket_visibility", schema=settings.db_schema), nullable=False, default=TicketVisibility.INTERNAL)
    due_date = Column(DateTime(timezone=True))
    created_by = Column(BigInteger)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_by = Column(BigInteger)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_by = Column(BigInteger)
    deleted_at = Column(DateTime(timezone=True))
    assigned_to = Column(BigInteger)

    categories = relationship("Category", secondary=ticket_categories, back_populates="tickets")
    labels = relationship("Label", secondary=ticket_labels, back_populates="tickets")
    ticket_template = relationship("TicketTemplate", back_populates="tickets")
    approval_template = relationship("ApprovalTemplate")
    attachments = relationship("TicketAttachment", back_populates="ticket")
    view_permissions = relationship("TicketViewPermission", back_populates="ticket")
    notes = relationship("TicketNote", back_populates="ticket")
    approval_process = relationship("ApprovalProcess", uselist=False, back_populates="ticket")
