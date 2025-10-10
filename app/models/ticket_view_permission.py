from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,  # Added
    ForeignKey,
    UniqueConstraint,
    func,  # Added
)
from sqlalchemy.orm import relationship

from app.config import settings
from app.models.base import Base


class TicketViewPermission(Base):
    __tablename__ = "ticket_view_permissions"
    __table_args__ = (UniqueConstraint("ticket_id", "user_id", "role_id"), {"schema": settings.db_schema})

    id = Column(BigInteger, primary_key=True)
    ticket_id = Column(BigInteger, ForeignKey(f"{settings.db_schema}.tickets.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger)
    role_id = Column(BigInteger)

    # Audit fields from schema
    created_by = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_by = Column(BigInteger)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    ticket = relationship("Ticket", back_populates="view_permissions")