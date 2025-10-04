from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    func,
)
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.enums import NotificationEvent


class NotificationRuleUser(Base):
    __tablename__ = "notification_rule_users"

    rule_id = Column(
        Integer,
        ForeignKey("notification_rules.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id = Column(Integer, primary_key=True)


class NotificationRuleRole(Base):
    __tablename__ = "notification_rule_roles"

    rule_id = Column(
        Integer,
        ForeignKey("notification_rules.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role_id = Column(Integer, primary_key=True)


class NotificationRule(Base):
    __tablename__ = "notification_rules"

    id = Column(Integer, primary_key=True)
    ticket_template_id = Column(Integer, ForeignKey("ticket_templates.id", ondelete="CASCADE"))
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"))
    notify_on_event = Column(Enum(NotificationEvent), nullable=False)
    created_by = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    ticket_template = relationship("TicketTemplate")
    ticket = relationship("Ticket")

    _users = relationship("NotificationRuleUser", cascade="all, delete-orphan")
    user_ids = association_proxy("users", "user_id", creator=lambda user_id: NotificationRuleUser(user_id=user_id))

    _roles = relationship("NotificationRuleRole", cascade="all, delete-orphan")
    role_ids = association_proxy("roles", "role_id", creator=lambda role_id: NotificationRuleRole(role_id=role_id))