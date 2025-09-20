from sqlalchemy import (
    BigInteger,
    Column,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.config import settings
from app.models.base import Base


class TicketViewPermission(Base):
    __tablename__ = "ticket_view_permissions"
    __table_args__ = (UniqueConstraint("ticket_id", "user_id", "role_id"), {"schema": settings.db_schema})

    id = Column(BigInteger, primary_key=True)
    ticket_id = Column(BigInteger, ForeignKey("ticket.tickets.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger)
    role_id = Column(BigInteger)

    ticket = relationship("Ticket", back_populates="view_permissions")
