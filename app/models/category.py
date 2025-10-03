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
from app.models.ticket import ticket_categories
from app.models.ticket_template import ticket_template_categories


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = {"schema": settings.db_schema}

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_by = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_by = Column(Integer)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_by = Column(Integer)
    deleted_at = Column(DateTime(timezone=True))

    ticket_templates = relationship("TicketTemplate", secondary=ticket_template_categories, back_populates="categories")
    tickets = relationship("Ticket", secondary=ticket_categories, back_populates="categories")
