import logging
import httpx

from app.config import settings

logger = logging.getLogger(__name__)

class MattermostClient:
    def __init__(self):
        self.webhook_url = settings.mattermost_webhook_url

    async def send_message(self, text: str, channel: str = None, username: str = "TicketBot"):
        """
        Sends a message to Mattermost.
        :param text: The message text. Can include Markdown.
        :param channel: The channel to post to (optional, overrides webhook's default).
        :param username: The username to post as (optional, overrides webhook's default).
        """
        if not self.webhook_url:
            logger.warning("Mattermost webhook URL is not configured. Cannot send message.")
            return False

        payload = {
            "text": text,
            "username": username
        }
        if channel:
            payload["channel"] = channel

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.webhook_url, json=payload)
                response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

            logger.info(f"Successfully sent message to Mattermost channel '{channel or 'default'}'.")
            return True
        except httpx.RequestError as e:
            logger.error(f"Error sending message to Mattermost: {e}")
            return False
        except httpx.HTTPStatusError as e:
            logger.error(
                f"Received non-200 response from Mattermost: {e.response.status_code} "
                f"| Response: {e.response.text}"
            )
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred while sending message to Mattermost: {e}")
            return False

# Single instance to be used across the application
mattermost_client = MattermostClient()