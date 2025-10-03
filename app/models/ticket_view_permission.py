from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.config import settings
from app.models.base import Base


class TicketViewPermission(Base):
    __tablename__ = "ticket_view_permissions"
    __table_args__ = {"schema": settings.db_schema, "extend_existing": True}

    ticket_id = Column(Integer, ForeignKey(f"{settings.db_schema}.tickets.id" if settings.db_schema else "tickets.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(Integer, primary_key=True)
    role_id = Column(Integer, primary_key=True)

    ticket = relationship("Ticket", back_populates="view_permissions")