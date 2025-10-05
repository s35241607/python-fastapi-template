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
from app.models.ticket import ticket_categories
from app.models.ticket_template import ticket_template_categories


class Category(Base, Auditable):
    __tablename__ = "categories"
    __table_args__ = {"schema": settings.db_schema}

    id = Column(BigInteger, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    is_deleted = Column(Boolean, nullable=False, default=False)

    ticket_templates = relationship("TicketTemplate", secondary=ticket_template_categories, back_populates="categories")
    tickets = relationship("Ticket", secondary=ticket_categories, back_populates="categories")