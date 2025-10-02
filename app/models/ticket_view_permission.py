from sqlalchemy import BigInteger, Column, ForeignKey
from sqlalchemy.orm import relationship

from app.config import settings
from app.models.base import Base


class TicketViewPermission(Base):
    __tablename__ = "ticket_view_permissions"
    __table_args__ = {"schema": settings.db_schema, "extend_existing": True}

    ticket_id = Column(BigInteger, ForeignKey(f"{settings.db_schema}.tickets.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(BigInteger, primary_key=True)
    role_id = Column(BigInteger, primary_key=True)

    ticket = relationship("Ticket", back_populates="view_permissions")