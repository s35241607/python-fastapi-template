from sqlalchemy import (
    BigInteger,
    Boolean,  # Added
    Column,
    DateTime,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.ticket import ticket_labels
from app.models.ticket_template import ticket_template_labels


class Label(Base):
    __tablename__ = "labels"
    __table_args__ = {"schema": "ticket"}

    id = Column(BigInteger, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    color = Column(String(7), nullable=False)
    description = Column(Text)
    created_by = Column(BigInteger)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_by = Column(BigInteger)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, nullable=False, default=False)  # Replaced soft delete columns

    ticket_templates = relationship("TicketTemplate", secondary=ticket_template_labels, back_populates="labels")
    tickets = relationship("Ticket", secondary=ticket_labels, back_populates="labels")