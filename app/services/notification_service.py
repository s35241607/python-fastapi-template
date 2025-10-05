import logging
from enum import Enum

from fastapi import Depends

from app.config import settings
from app.models.ticket import Ticket
from app.repositories.notification_rule_repository import NotificationRuleRepository
from app.schemas.ticket import TicketRead
from app.utils.kafka_producer import kafka_producer_client
from app.utils.mattermost_client import mattermost_client
from app.utils.smtp_client import smtp_client

logger = logging.getLogger(__name__)


class NotificationEvent(str, Enum):
    """
    Enum for notification trigger events.
    Corresponds to the `notification_event` enum in the database.
    """
    ON_CREATE = "on_create"
    ON_STATUS_CHANGE = "on_status_change"
    ON_CLOSE = "on_close"
    ON_NEW_COMMENT = "on_new_comment"
    # Note: 'assignee_change' could be mapped to 'on_status_change'
    # or have its own event type if the schema is extended.


class NotificationService:
    def __init__(
        self,
        notification_repo: NotificationRuleRepository = Depends(NotificationRuleRepository),
    ):
        self.notification_repo = notification_repo

    def _format_mattermost_message(self, event: NotificationEvent, ticket: Ticket | TicketRead) -> str:
        return (
            f"**Ticket Event: {event.name.replace('_', ' ').title()}**\n"
            f"Ticket #{ticket.ticket_no}: *{ticket.title}*\n"
            f"Status: `{ticket.status}` | Priority: `{ticket.priority}`"
        )

    def _format_email_subject(self, event: NotificationEvent, ticket: Ticket | TicketRead) -> str:
        return f"[Ticket #{ticket.ticket_no}] Event: {event.name.replace('_', ' ').title()}"

    def _format_email_body(self, event: NotificationEvent, ticket: Ticket | TicketRead) -> str:
        return f"""
        <html>
        <body>
            <h2>Ticket Event Notification</h2>
            <p>This is a notification for an event on Ticket <strong>#{ticket.ticket_no}</strong>.</p>
            <ul>
                <li><strong>Title:</strong> {ticket.title}</li>
                <li><strong>Event:</strong> {event.name.replace('_', ' ').title()}</li>
                <li><strong>Status:</strong> {ticket.status}</li>
                <li><strong>Priority:</strong> {ticket.priority}</li>
            </ul>
            <p>Thank you.</p>
        </body>
        </html>
        """

    def _format_kafka_payload(self, event: NotificationEvent, ticket: Ticket | TicketRead, user_ids: set, role_ids: set) -> dict:
        return {
            "event_type": event.value,
            "ticket": {
                "id": ticket.id,
                "ticket_no": ticket.ticket_no,
                "title": ticket.title,
                "status": ticket.status,
                "priority": ticket.priority,
            },
            "notify_users": list(user_ids),
            "notify_roles": list(role_ids),
        }

    async def trigger_event(self, event: NotificationEvent, ticket: Ticket | TicketRead, original_ticket_data: dict = None):
        logger.info(f"Attempting to trigger notification event '{event.value}' for ticket ID {ticket.id}")

        rules = await self.notification_repo.get_by_event(
            event=event.value,
            ticket_id=ticket.id,
            ticket_template_id=ticket.ticket_template_id,
        )

        if not rules:
            logger.info(f"No notification rules found for event '{event.value}' on ticket {ticket.id}.")
            return

        user_ids_to_notify = set()
        role_ids_to_notify = set()
        for rule in rules:
            user_ids_to_notify.update(rule.user_ids)
            role_ids_to_notify.update(rule.role_ids)

        if not user_ids_to_notify and not role_ids_to_notify:
            logger.info(f"Rules found for event '{event.value}' on ticket {ticket.id}, but no users or roles are assigned.")
            return

        # 1. Send to Kafka (primary mechanism)
        kafka_payload = self._format_kafka_payload(event, ticket, user_ids_to_notify, role_ids_to_notify)
        kafka_producer_client.send_message(
            topic=settings.kafka_notification_topic,
            message=kafka_payload
        )

        # 2. Send to Mattermost
        mattermost_message = self._format_mattermost_message(event, ticket)
        await mattermost_client.send_message(text=mattermost_message)

        # 3. Send to SMTP
        if user_ids_to_notify:
            # This is a placeholder as we don't have a user service to resolve emails.
            # In a real system, you would fetch user details here.
            recipient_emails = [f"user_{user_id}@example.com" for user_id in user_ids_to_notify]
            logger.warning(f"User email resolution is not implemented. Using placeholder emails: {recipient_emails}")

            email_subject = self._format_email_subject(event, ticket)
            email_body = self._format_email_body(event, ticket)

            smtp_client.send_email(
                to_emails=recipient_emails,
                subject=email_subject,
                html_content=email_body
            )
        else:
            logger.info("No specific user IDs found for email notification.")