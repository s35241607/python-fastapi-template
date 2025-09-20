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
        "rule_id", BigInteger, ForeignKey(f"{settings.db_schema}.notification_rules.id", ondelete="CASCADE"), primary_key=True
    ),
    Column("user_id", BigInteger, primary_key=True),
    schema=settings.db_schema,
)

notification_rule_roles = Table(
    "notification_rule_roles",
    Base.metadata,
    Column(
        "rule_id", BigInteger, ForeignKey(f"{settings.db_schema}.notification_rules.id", ondelete="CASCADE"), primary_key=True
    ),
    Column("role_id", BigInteger, primary_key=True),
    schema=settings.db_schema,
)


class NotificationRule(Base):
    __tablename__ = "notification_rules"
    __table_args__ = {"schema": settings.db_schema}

    id = Column(BigInteger, primary_key=True)
    ticket_template_id = Column(BigInteger, ForeignKey(f"{settings.db_schema}.ticket_templates.id", ondelete="CASCADE"))
    ticket_id = Column(BigInteger, ForeignKey(f"{settings.db_schema}.tickets.id", ondelete="CASCADE"))
    notify_on_event = Column(Enum(NotificationEvent, name="notification_event", schema=settings.db_schema), nullable=False)
    created_by = Column(BigInteger)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    ticket_template = relationship("TicketTemplate")
    ticket = relationship("Ticket")
