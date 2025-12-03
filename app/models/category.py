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

from app.config import settings
from app.models.base import Base
from app.models.ticket import ticket_categories
from app.models.ticket_template import ticket_template_categories


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = {"schema": settings.DB_SCHEMA}

    id = Column(BigInteger, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)  # Added unique=True
    description = Column(Text)
    created_by = Column(BigInteger)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_by = Column(BigInteger)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, nullable=False, default=False)  # Replaced soft delete columns

    ticket_templates = relationship("TicketTemplate", secondary=ticket_template_categories, back_populates="categories")
    tickets = relationship("Ticket", secondary=ticket_categories, back_populates="categories")
