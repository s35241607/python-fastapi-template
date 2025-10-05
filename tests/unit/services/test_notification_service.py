import unittest
from unittest.mock import MagicMock, AsyncMock, patch

from app.schemas.ticket import TicketRead
from app.services.notification_service import NotificationEvent, NotificationService


# Mock settings before other imports
@patch('app.config.settings')
class TestNotificationService(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        # Mock dependencies
        self.mock_notification_repo = MagicMock()
        self.mock_notification_repo.get_by_event = AsyncMock()

        # Instantiate the service with mocked dependencies
        self.notification_service = NotificationService(
            notification_repo=self.mock_notification_repo
        )

        # Mock ticket data for testing
        self.mock_ticket = TicketRead(
            id=1,
            ticket_no="T-123",
            title="Test Ticket",
            status="open",
            priority="medium",
            created_at="2023-01-01T12:00:00Z",
            ticket_template_id=10,
            categories=[],
            labels=[],
            notes=[]
        )

    @patch('app.services.notification_service.kafka_producer_client')
    @patch('app.services.notification_service.mattermost_client')
    @patch('app.services.notification_service.smtp_client')
    async def test_trigger_event_success(self, mock_smtp_client, mock_mattermost_client, mock_kafka_client, mock_settings):
        """Test successful triggering of all notification channels."""
        # Arrange
        mock_rule = MagicMock()
        mock_rule.user_ids = {101, 102}
        mock_rule.role_ids = {201}
        self.mock_notification_repo.get_by_event.return_value = [mock_rule]

        mock_kafka_client.send_message = MagicMock()
        mock_mattermost_client.send_message = AsyncMock()
        mock_smtp_client.send_email = MagicMock()

        # Act
        await self.notification_service.trigger_event(NotificationEvent.ON_CREATE, self.mock_ticket)

        # Assert
        # 1. Check if repo was called correctly
        self.mock_notification_repo.get_by_event.assert_awaited_once_with(
            event=NotificationEvent.ON_CREATE.value,
            ticket_id=self.mock_ticket.id,
            ticket_template_id=self.mock_ticket.ticket_template_id
        )

        # 2. Check Kafka call
        mock_kafka_client.send_message.assert_called_once()
        kafka_call_args = mock_kafka_client.send_message.call_args[1]
        self.assertEqual(kafka_call_args['topic'], mock_settings.kafka_notification_topic)
        self.assertEqual(kafka_call_args['message']['event_type'], 'on_create')
        self.assertEqual(kafka_call_args['message']['ticket']['id'], 1)
        self.assertEqual(set(kafka_call_args['message']['notify_users']), {101, 102})
        self.assertEqual(set(kafka_call_args['message']['notify_roles']), {201})

        # 3. Check Mattermost call
        mock_mattermost_client.send_message.assert_awaited_once()
        mattermost_call_args = mock_mattermost_client.send_message.call_args[1]
        self.assertIn("Ticket Event: On Create", mattermost_call_args['text'])
        self.assertIn("Ticket #T-123", mattermost_call_args['text'])

        # 4. Check SMTP call
        mock_smtp_client.send_email.assert_called_once()
        smtp_call_args = mock_smtp_client.send_email.call_args[1]
        self.assertEqual(set(smtp_call_args['to_emails']), {"user_101@example.com", "user_102@example.com"})
        self.assertIn("[Ticket #T-123]", smtp_call_args['subject'])
        self.assertIn("<h2>Ticket Event Notification</h2>", smtp_call_args['html_content'])

    async def test_trigger_event_no_rules_found(self, mock_settings):
        """Test that no notifications are sent if no rules are found."""
        # Arrange
        self.mock_notification_repo.get_by_event.return_value = []

        # Act
        await self.notification_service.trigger_event(NotificationEvent.ON_CREATE, self.mock_ticket)

        # Assert
        # We can't easily check that the clients were *not* called without patching them,
        # but we can verify the log message.
        with self.assertLogs('app.services.notification_service', level='INFO') as cm:
            # Re-run the action to capture logs
            await self.notification_service.trigger_event(NotificationEvent.ON_CREATE, self.mock_ticket)
            self.assertIn("No notification rules found", cm.output[1])

    async def test_trigger_event_no_users_or_roles_in_rules(self, mock_settings):
        """Test that no notifications are sent if rules have no assigned users/roles."""
        # Arrange
        mock_rule = MagicMock()
        mock_rule.user_ids = set()
        mock_rule.role_ids = set()
        self.mock_notification_repo.get_by_event.return_value = [mock_rule]

        # Act & Assert
        with self.assertLogs('app.services.notification_service', level='INFO') as cm:
            await self.notification_service.trigger_event(NotificationEvent.ON_CREATE, self.mock_ticket)
            self.assertIn("no users or roles are assigned", cm.output[1])

if __name__ == '__main__':
    unittest.main()