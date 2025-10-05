import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

from app.config import settings

logger = logging.getLogger(__name__)

class SMTPClient:
    def __init__(self):
        self.settings = settings

    def send_email(self, to_emails: List[str], subject: str, html_content: str, cc_emails: List[str] = None):
        if self.settings.smtp_test_mode:
            logger.info("SMTP Test Mode is enabled. Email will not be sent.")
            logger.info(f"  - TO: {', '.join(to_emails)}")
            if cc_emails:
                logger.info(f"  - CC: {', '.join(cc_emails)}")
            logger.info(f"  - Subject: {subject}")
            logger.info(f"  - Body:\n{html_content}")
            return True

        if not self.settings.smtp_host:
            logger.error("SMTP host is not configured. Cannot send email.")
            return False

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.settings.smtp_sender
        msg['To'] = ", ".join(to_emails)

        recipients = to_emails
        if cc_emails:
            msg['Cc'] = ", ".join(cc_emails)
            recipients.extend(cc_emails)

        msg.attach(MIMEText(html_content, 'html'))

        try:
            with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port) as server:
                if self.settings.smtp_user and self.settings.smtp_password:
                    server.starttls()
                    server.login(self.settings.smtp_user, self.settings.smtp_password)

                server.sendmail(self.settings.smtp_sender, recipients, msg.as_string())
                logger.info(f"Successfully sent email to {', '.join(recipients)}")
                return True
        except smtplib.SMTPException as e:
            logger.error(f"Failed to send email via SMTP: {e}")
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred while sending email: {e}")
            return False

# Single instance to be used across the application
smtp_client = SMTPClient()