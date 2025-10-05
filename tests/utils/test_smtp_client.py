import unittest
from unittest.mock import patch, MagicMock, ANY

# Patch settings before import
with patch('app.config.settings', MagicMock()) as mock_settings:
    mock_settings.smtp_test_mode = False
    mock_settings.smtp_host = "smtp.mock.com"
    mock_settings.smtp_port = 587
    mock_settings.smtp_user = "user"
    mock_settings.smtp_password = "password"
    mock_settings.smtp_sender = "sender@mock.com"
    from app.utils.smtp_client import SMTPClient

class TestSMTPClient(unittest.TestCase):

    def setUp(self):
        # Reset settings for each test to ensure isolation
        self.mock_settings = MagicMock()
        self.mock_settings.smtp_host = "smtp.mock.com"
        self.mock_settings.smtp_port = 587
        self.mock_settings.smtp_user = "user"
        self.mock_settings.smtp_password = "password"
        self.mock_settings.smtp_sender = "sender@mock.com"
        self.mock_settings.smtp_test_mode = False

        self.client = SMTPClient()
        self.client.settings = self.mock_settings

    @patch('app.utils.smtp_client.smtplib.SMTP')
    def test_send_email_normal_mode(self, MockSMTP):
        """Test sending email in normal mode."""
        mock_server = MockSMTP.return_value.__enter__.return_value

        to_emails = ["test@example.com"]
        cc_emails = ["cc@example.com"]
        subject = "Test Subject"
        html_content = "<p>Hello</p>"

        result = self.client.send_email(to_emails, subject, html_content, cc_emails)

        self.assertTrue(result)
        MockSMTP.assert_called_once_with("smtp.mock.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("user", "password")
        mock_server.sendmail.assert_called_once_with(
            "sender@mock.com",
            ["test@example.com", "cc@example.com"],
            ANY  # The message string is complex to match exactly, so we check its components
        )

        # Check message headers
        sent_message = mock_server.sendmail.call_args[0][2]
        self.assertIn("Subject: Test Subject", sent_message)
        self.assertIn("From: sender@mock.com", sent_message)
        self.assertIn("To: test@example.com", sent_message)
        self.assertIn("Cc: cc@example.com", sent_message)

    def test_send_email_test_mode(self):
        """Test that email is not sent in test mode, but logged."""
        self.mock_settings.smtp_test_mode = True
        self.client.settings = self.mock_settings

        to_emails = ["test@example.com"]
        cc_emails = ["cc@example.com"]

        with self.assertLogs('app.utils.smtp_client', level='INFO') as cm:
            result = self.client.send_email(to_emails, "Subject", "Body", cc_emails)
            self.assertTrue(result)
            self.assertIn("SMTP Test Mode is enabled", cm.output[0])
            self.assertIn("TO: test@example.com", cm.output[1])
            self.assertIn("CC: cc@example.com", cm.output[2])

    def test_send_email_no_host(self):
        """Test behavior when SMTP host is not configured."""
        self.mock_settings.smtp_host = None
        self.client.settings = self.mock_settings

        with self.assertLogs('app.utils.smtp_client', level='ERROR') as cm:
            result = self.client.send_email(["test@example.com"], "Subject", "Body")
            self.assertFalse(result)
            self.assertIn("SMTP host is not configured", cm.output[0])

    @patch('app.utils.smtp_client.smtplib.SMTP', side_effect=Exception("SMTP connection failed"))
    def test_send_email_smtp_exception(self, MockSMTP):
        """Test handling of SMTP exceptions."""
        with self.assertLogs('app.utils.smtp_client', level='ERROR') as cm:
            result = self.client.send_email(["test@example.com"], "Subject", "Body")
            self.assertFalse(result)
            self.assertIn("An unexpected error occurred while sending email: SMTP connection failed", cm.output[0])

if __name__ == '__main__':
    unittest.main()