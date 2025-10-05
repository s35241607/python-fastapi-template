import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import httpx

# Patch settings before import
with patch('app.config.settings', MagicMock()) as mock_settings:
    mock_settings.mattermost_webhook_url = "https://mock.mattermost.com/hooks/somehook"
    from app.utils.mattermost_client import MattermostClient

class TestMattermostClient(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.mock_settings = MagicMock()
        self.mock_settings.mattermost_webhook_url = "https://mock.mattermost.com/hooks/somehook"

        self.client = MattermostClient()
        self.client.webhook_url = self.mock_settings.mattermost_webhook_url

    @patch('app.utils.mattermost_client.httpx.AsyncClient')
    async def test_send_message_success(self, MockAsyncClient):
        """Test successful message sending to Mattermost."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.raise_for_status = MagicMock()

        mock_async_client = AsyncMock()
        mock_async_client.post.return_value = mock_response

        # This is how you mock an async context manager
        MockAsyncClient.return_value.__aenter__.return_value = mock_async_client

        result = await self.client.send_message("Hello, world!", channel="test-channel")

        self.assertTrue(result)
        mock_async_client.post.assert_awaited_once_with(
            "https://mock.mattermost.com/hooks/somehook",
            json={"text": "Hello, world!", "username": "TicketBot", "channel": "test-channel"}
        )
        mock_response.raise_for_status.assert_called_once()

    async def test_send_message_no_webhook_url(self):
        """Test that nothing is sent if the webhook URL is not configured."""
        self.client.webhook_url = None

        with self.assertLogs('app.utils.mattermost_client', level='WARNING') as cm:
            result = await self.client.send_message("Hello, world!")
            self.assertFalse(result)
            self.assertIn("Mattermost webhook URL is not configured", cm.output[0])

    @patch('app.utils.mattermost_client.httpx.AsyncClient')
    async def test_send_message_request_error(self, MockAsyncClient):
        """Test handling of httpx.RequestError."""
        mock_async_client = AsyncMock()
        mock_async_client.post.side_effect = httpx.RequestError("Network error", request=MagicMock())
        MockAsyncClient.return_value.__aenter__.return_value = mock_async_client

        with self.assertLogs('app.utils.mattermost_client', level='ERROR') as cm:
            result = await self.client.send_message("Hello, world!")
            self.assertFalse(result)
            self.assertIn("Error sending message to Mattermost: Network error", cm.output[0])

    @patch('app.utils.mattermost_client.httpx.AsyncClient')
    async def test_send_message_http_status_error(self, MockAsyncClient):
        """Test handling of httpx.HTTPStatusError."""
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 400
        mock_response.text = "Invalid payload"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Bad Request", request=MagicMock(), response=mock_response
        )

        mock_async_client = AsyncMock()
        mock_async_client.post.return_value = mock_response
        MockAsyncClient.return_value.__aenter__.return_value = mock_async_client

        with self.assertLogs('app.utils.mattermost_client', level='ERROR') as cm:
            result = await self.client.send_message("Hello, world!")
            self.assertFalse(result)
            self.assertIn("Received non-200 response from Mattermost: 400 | Response: Invalid payload", cm.output[0])

if __name__ == '__main__':
    unittest.main()