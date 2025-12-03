from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Table,
    func,
)
from sqlalchemy.orm import relationship

from app.config import settings
from app.models.base import Base
from app.models.enums import NotificationEvent

notification_rule_users = Table(
    "notification_rule_users",
    Base.metadata,
    Column(
        "rule_id", BigInteger, ForeignKey(f"{settings.DB_SCHEMA}.notification_rules.id", ondelete="CASCADE"), primary_key=True
    ),
    Column("user_id", BigInteger, primary_key=True),
    schema=settings.DB_SCHEMA,
)

notification_rule_roles = Table(
    "notification_rule_roles",
    Base.metadata,
    Column(
        "rule_id", BigInteger, ForeignKey(f"{settings.DB_SCHEMA}.notification_rules.id", ondelete="CASCADE"), primary_key=True
    ),
    Column("role_id", BigInteger, primary_key=True),
    schema=settings.DB_SCHEMA,
)


class NotificationRule(Base):
    __tablename__ = "notification_rules"
    __table_args__ = {"schema": settings.DB_SCHEMA}

    id = Column(BigInteger, primary_key=True)
    ticket_template_id = Column(BigInteger, ForeignKey(f"{settings.DB_SCHEMA}.ticket_templates.id", ondelete="CASCADE"))
    ticket_id = Column(BigInteger, ForeignKey(f"{settings.DB_SCHEMA}.tickets.id", ondelete="CASCADE"))
    notify_on_event = Column(Enum(NotificationEvent, name="notification_event", schema=settings.DB_SCHEMA), nullable=False)
    created_by = Column(BigInteger)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    ticket_template = relationship("TicketTemplate")
    ticket = relationship("Ticket")
