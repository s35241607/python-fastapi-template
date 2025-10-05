from sqlalchemy import (
    BigInteger,
    Column,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.config import settings
from app.models.base import Base, Auditable


class TicketViewPermission(Base, Auditable):
    __tablename__ = "ticket_view_permissions"
    __table_args__ = (
        UniqueConstraint("ticket_id", "user_id", "role_id", name="uq_ticket_view_permissions_ticket_user_role"),
        {"schema": settings.db_schema, "extend_existing": True},
    )

    # The table does not have a single primary key column in the schema.
    # We need to define the columns that make up the unique constraint,
    # but SQLAlchemy requires at least one primary key. We will let the DB enforce uniqueness.
    # For mapping purposes, we can set a pseudo-primary key, but it's better to reflect the schema.
    # The schema has a UNIQUE constraint, not a composite PK.
    # Let's add a proper primary key as suggested by good practice, and align the schema later if needed.
    id = Column(BigInteger, primary_key=True, index=True)
    ticket_id = Column(BigInteger, ForeignKey(f"{settings.db_schema}.tickets.id" if settings.db_schema else "tickets.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger)
    role_id = Column(BigInteger)

    ticket = relationship("Ticket", back_populates="view_permissions")