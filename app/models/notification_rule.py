from sqlalchemy import (
    Column,
    Enum,
    ForeignKey,
    BigInteger,
)
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from app.config import settings
from app.models.base import Base, Auditable
from app.models.enums import NotificationEvent


class NotificationRuleUser(Base, Auditable):
    __tablename__ = "notification_rule_users"
    __table_args__ = {"schema": settings.db_schema, "extend_existing": True}

    rule_id = Column(
        BigInteger,
        ForeignKey(f"{settings.db_schema}.notification_rules.id" if settings.db_schema else "notification_rules.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id = Column(BigInteger, primary_key=True)


class NotificationRuleRole(Base, Auditable):
    __tablename__ = "notification_rule_roles"
    __table_args__ = {"schema": settings.db_schema, "extend_existing": True}

    rule_id = Column(
        BigInteger,
        ForeignKey(f"{settings.db_schema}.notification_rules.id" if settings.db_schema else "notification_rules.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role_id = Column(BigInteger, primary_key=True)


class NotificationRule(Base, Auditable):
    __tablename__ = "notification_rules"
    __table_args__ = {"schema": settings.db_schema, "extend_existing": True}

    id = Column(BigInteger, primary_key=True)
    ticket_template_id = Column(BigInteger, ForeignKey(f"{settings.db_schema}.ticket_templates.id" if settings.db_schema else "ticket_templates.id", ondelete="CASCADE"))
    ticket_id = Column(BigInteger, ForeignKey(f"{settings.db_schema}.tickets.id" if settings.db_schema else "tickets.id", ondelete="CASCADE"))
    notify_on_event = Column(Enum(NotificationEvent, name="notification_event", schema=settings.db_schema), nullable=False)

    ticket_template = relationship("TicketTemplate", back_populates="notification_rules")
    # A ticket can have notification rules, but the back_populates should be defined on the Ticket model if needed.
    # For now, we assume a one-way relationship from the rule to the ticket.
    ticket = relationship("Ticket")

    _users = relationship("NotificationRuleUser", cascade="all, delete-orphan", lazy="selectin")
    user_ids = association_proxy("_users", "user_id", creator=lambda user_id: NotificationRuleUser(user_id=user_id))

    _roles = relationship("NotificationRuleRole", cascade="all, delete-orphan", lazy="selectin")
    role_ids = association_proxy("_roles", "role_id", creator=lambda role_id: NotificationRuleRole(role_id=role_id))