import logging
from enum import Enum

from fastapi import Depends

from app.models.ticket import Ticket
from app.repositories.notification_rule_repository import NotificationRuleRepository
from app.schemas.ticket import TicketRead

logger = logging.getLogger(__name__)


class NotificationEvent(str, Enum):
    """
    Enum for notification trigger events.
    These values should correspond to the `notify_on_event` column in the `notification_rules` table.
    """
    TICKET_CREATED = "ticket_created"
    STATUS_CHANGED_TO_WAITING_APPROVAL = "status_changed_to_waiting_approval"
    STATUS_CHANGED_TO_REJECTED = "status_changed_to_rejected"
    STATUS_CHANGED_TO_OPEN = "status_changed_to_open"
    STATUS_CHANGED_TO_IN_PROGRESS = "status_changed_to_in_progress"
    STATUS_CHANGED_TO_RESOLVED = "status_changed_to_resolved"
    STATUS_CHANGED_TO_CLOSED = "status_changed_to_closed"
    ASSIGNEE_CHANGED = "assignee_changed"
    COMMENT_ADDED = "comment_added"


class NotificationService:
    def __init__(
        self,
        notification_repo: NotificationRuleRepository = Depends(NotificationRuleRepository),
    ):
        self.notification_repo = notification_repo

    async def trigger_event(self, event: NotificationEvent, ticket: Ticket | TicketRead):
        """
        Triggers a notification event for a given ticket.
        This is the main entry point for other services to call.
        """
        logger.info(f"Attempting to trigger notification event '{event.value}' for ticket ID {ticket.id}")

        # In a real-world scenario, this service would be much more complex. It would:
        # 1. Find all notification rules matching the event for the ticket_id or its template_id.
        # 2. Aggregate all user_ids and role_ids from the matching rules.
        # 3. Resolve role_ids to a list of user_ids (potentially by calling a separate user/identity service).
        # 4. Deduplicate the final list of user_ids to ensure no one receives multiple notifications for the same event.
        # 5. Construct a notification payload (e.g., email content, Slack message).
        # 6. Push the notification task to a robust message queue (e.g., Kafka, RabbitMQ) for asynchronous processing.
        #
        # For the purpose of this implementation, we will simply log the action
        # to demonstrate that the trigger point is correctly placed and the logic is invoked.

        # A simplified logic to demonstrate the concept:
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

        # In a real system, you would now resolve role_ids to user_ids and merge them.
        # For now, we'll just log them separately.

        if user_ids_to_notify or role_ids_to_notify:
            logger.info(
                f"NOTIFICATION: Event '{event.value}' on Ticket ID {ticket.id}. "
                f"Would notify User IDs: {list(user_ids_to_notify)} and Role IDs: {list(role_ids_to_notify)}"
            )
        else:
            logger.info(f"Rules found for event '{event.value}' on ticket {ticket.id}, but no specific users or roles assigned to them.")