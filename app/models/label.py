from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.config import settings
from app.models.base import Base
from app.models.ticket import ticket_labels
from app.models.ticket_template import ticket_template_labels


class Label(Base):
    __tablename__ = "labels"
    __table_args__ = {"schema": settings.db_schema}

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    color = Column(String(7), nullable=False)
    description = Column(Text)
    created_by = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    ticket_templates = relationship("TicketTemplate", secondary=ticket_template_labels, back_populates="labels")
    tickets = relationship("Ticket", secondary=ticket_labels, back_populates="labels")
    updated_by = Column(Integer)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_by = Column(Integer)
    deleted_at = Column(DateTime(timezone=True))
