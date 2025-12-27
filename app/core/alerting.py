"""
Alerting system for sending notifications to external services.

This module provides:
- Mattermost webhook integration for real-time alerts
- Extensible alerter base class for future integrations
- Async-first design for non-blocking alerts
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from enum import Enum

import httpx
from loguru import logger

from app.config import settings
from app.core.logging import get_correlation_id


class AlertLevel(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class BaseAlerter(ABC):
    """Base class for alerting integrations."""

    @abstractmethod
    async def send_alert(
        self,
        title: str,
        message: str,
        level: AlertLevel = AlertLevel.ERROR,
        fields: dict[str, object] | None = None,
    ) -> bool:
        """Send an alert notification."""
        ...


class MattermostAlerter(BaseAlerter):
    """
    Send alerts to Mattermost via incoming webhook.

    Mattermost webhook format:
    https://developers.mattermost.com/integrate/webhooks/incoming/
    """

    def __init__(
        self,
        webhook_url: str | None = None,
        channel: str | None = None,
        username: str = "Alert Bot",
        icon_emoji: str = ":warning:",
    ):
        self.webhook_url = webhook_url or settings.MATTERMOST_WEBHOOK_URL
        self.channel = channel or settings.MATTERMOST_CHANNEL
        self.username = username
        self.icon_emoji = icon_emoji

    def _get_color_for_level(self, level: AlertLevel) -> str:
        """Get attachment color based on alert level."""
        colors = {
            AlertLevel.INFO: "#36a64f",      # Green
            AlertLevel.WARNING: "#daa038",    # Orange
            AlertLevel.ERROR: "#d00000",      # Red
            AlertLevel.CRITICAL: "#8b0000",   # Dark Red
        }
        return colors.get(level, "#808080")

    def _get_emoji_for_level(self, level: AlertLevel) -> str:
        """Get emoji prefix based on alert level."""
        emojis = {
            AlertLevel.INFO: "ℹ️",
            AlertLevel.WARNING: "⚠️",
            AlertLevel.ERROR: "🚨",
            AlertLevel.CRITICAL: "🔥",
        }
        return emojis.get(level, "📢")

    async def send_alert(
        self,
        title: str,
        message: str,
        level: AlertLevel = AlertLevel.ERROR,
        fields: dict[str, object] | None = None,
    ) -> bool:
        """
        Send an alert to Mattermost.

        Args:
            title: Alert title
            message: Alert message/description
            level: Severity level
            fields: Additional key-value fields to display

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.webhook_url:
            logger.debug("Mattermost webhook URL not configured, skipping alert")
            return False

        if not settings.ALERT_ENABLED:
            logger.debug("Alerting disabled, skipping alert")
            return False

        # Build attachment fields
        attachment_fields = []

        # Add timestamp
        attachment_fields.append({
            "short": True,
            "title": "Time",
            "value": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC"),
        })

        # Add environment
        attachment_fields.append({
            "short": True,
            "title": "Environment",
            "value": settings.ENVIRONMENT,
        })

        # Add correlation ID if available
        correlation_id = get_correlation_id()
        if correlation_id:
            attachment_fields.append({
                "short": True,
                "title": "Correlation ID",
                "value": f"`{correlation_id[:8]}...`",
            })

        # Add custom fields
        if fields:
            for key, value in fields.items():
                attachment_fields.append({
                    "short": True,
                    "title": key.replace("_", " ").title(),
                    "value": str(value),
                })

        # Build payload
        emoji = self._get_emoji_for_level(level)
        payload = {
            "username": self.username,
            "icon_emoji": self.icon_emoji,
            "attachments": [
                {
                    "fallback": f"{emoji} {title}: {message}",
                    "color": self._get_color_for_level(level),
                    "title": f"{emoji} {title}",
                    "text": message,
                    "fields": attachment_fields,
                }
            ],
        }

        # Add channel override if specified
        if self.channel:
            payload["channel"] = self.channel

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.webhook_url, json=payload)
                response.raise_for_status()
                logger.debug(f"Alert sent to Mattermost: {title}")
                return True
        except httpx.HTTPError as e:
            logger.error(f"Failed to send Mattermost alert: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending Mattermost alert: {e}")
            return False


# Default alerter instance
_default_alerter: MattermostAlerter | None = None


def get_alerter() -> MattermostAlerter:
    """Get the default alerter instance."""
    global _default_alerter
    if _default_alerter is None:
        _default_alerter = MattermostAlerter()
    return _default_alerter


async def send_alert(
    title: str,
    message: str,
    level: AlertLevel = AlertLevel.ERROR,
    fields: dict[str, object] | None = None,
) -> bool:
    """
    Convenience function to send an alert using the default alerter.

    Args:
        title: Alert title
        message: Alert message/description
        level: Severity level (default: ERROR)
        fields: Additional key-value fields to display

    Returns:
        True if sent successfully, False otherwise
    """
    alerter = get_alerter()
    return await alerter.send_alert(title, message, level, fields)


__all__ = [
    "AlertLevel",
    "BaseAlerter",
    "MattermostAlerter",
    "get_alerter",
    "send_alert",
]
