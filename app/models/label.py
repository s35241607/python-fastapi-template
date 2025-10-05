from sqlalchemy import (
    Boolean,
    Column,
    BigInteger,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.config import settings
from app.models.base import Base, Auditable
from app.models.ticket import ticket_labels
from app.models.ticket_template import ticket_template_labels


class Label(Base, Auditable):
    __tablename__ = "labels"
    __table_args__ = {"schema": settings.db_schema}

    id = Column(BigInteger, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    color = Column(String(7), nullable=False)
    description = Column(Text)
    is_deleted = Column(Boolean, nullable=False, default=False)

    ticket_templates = relationship("TicketTemplate", secondary=ticket_template_labels, back_populates="labels")
    tickets = relationship("Ticket", secondary=ticket_labels, back_populates="labels")