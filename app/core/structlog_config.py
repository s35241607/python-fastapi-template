"""
Enterprise-grade structured logging configuration using structlog.

This module provides:
- Unified logging for all application components (FastAPI, Uvicorn, SQLAlchemy)
- Structured JSON logging for production environments (Loki/Grafana compatible)
- Colored console logging for development
- Automatic request_id and user_id injection via contextvars
- Integration with asgi-correlation-id for X-Request-ID propagation
"""

from __future__ import annotations

import logging
import sys
from contextvars import ContextVar
from typing import TYPE_CHECKING

import structlog
from asgi_correlation_id import correlation_id

if TYPE_CHECKING:
    from structlog.typing import EventDict, Processor, WrappedLogger

from app.config import settings

# Context variable for user_id (request_id is managed by asgi-correlation-id)
user_id_ctx: ContextVar[str | None] = ContextVar("user_id", default=None)


def get_request_id() -> str | None:
    """Get the current request ID from asgi-correlation-id."""
    return correlation_id.get()


def get_user_id() -> str | None:
    """Get the current user ID from context."""
    return user_id_ctx.get()


def set_user_id(user_id: str | None) -> None:
    """Set the user ID for the current context."""
    user_id_ctx.set(user_id)


def clear_user_id() -> None:
    """Clear the user ID from the current context."""
    user_id_ctx.set(None)


def add_request_context(
    logger: WrappedLogger, method_name: str, event_dict: EventDict
) -> EventDict:
    """
    Processor that adds request_id and user_id to every log entry.

    These values are automatically populated from contextvars set by middleware.
    """
    # Always try to get request_id from asgi-correlation-id
    request_id = correlation_id.get()
    user_id = user_id_ctx.get()

    # Add to event_dict if present
    if request_id:
        event_dict["request_id"] = request_id
    if user_id:
        event_dict["user_id"] = user_id

    return event_dict


def drop_color_message_key(
    logger: WrappedLogger, method_name: str, event_dict: EventDict
) -> EventDict:
    """
    Remove the 'color_message' key from uvicorn logs.

    Uvicorn adds a 'color_message' key with ANSI codes which we don't need in JSON.
    """
    event_dict.pop("color_message", None)
    return event_dict


def inject_app_context(
    logger: WrappedLogger, method_name: str, event_dict: EventDict
) -> EventDict:
    """
    Inject static application context so that every log line has standard fields
    for indexing in Grafana Loki (e.g. app_name, environment).
    """
    event_dict["app_name"] = settings.APP_NAME
    event_dict["app_version"] = settings.APP_VERSION
    event_dict["environment"] = settings.ENVIRONMENT
    return event_dict


def setup_logging() -> None:
    """
    Initialize the logging system with structlog.

    This function should be called once at application startup,
    BEFORE creating the FastAPI app instance.

    The configuration:
    - Development: Colored console output with human-readable format
    - Production: JSON Lines format for Loki/Promtail ingestion
    """
    # Determine log level
    log_level = settings.LOG_LEVEL.upper()
    numeric_level = getattr(logging, log_level, logging.INFO)

    # Shared processors for both structlog and stdlib logging
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        inject_app_context,  # Add static app info (env, version)
        add_request_context,  # Add dynamic request info (request_id, user_id)
        structlog.stdlib.ExtraAdder(),
        drop_color_message_key,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.LOG_RENDER_JSON:
        # Production: JSON format for Loki
        shared_processors.append(
            structlog.processors.format_exc_info,
        )
        renderer: Processor = structlog.processors.JSONRenderer()
    else:
        # Development: Colored console output
        renderer = structlog.dev.ConsoleRenderer(
            colors=True,
            exception_formatter=structlog.dev.plain_traceback,
        )

    # Configure structlog
    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Create formatter for stdlib logging
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    # Configure root handler - use stdout for all logs
    root_handler = logging.StreamHandler(sys.stdout)
    root_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(root_handler)
    root_logger.setLevel(numeric_level)

    # Configure specific library loggers to reduce noise and prevent raw tracebacks
    _configure_library_loggers(numeric_level)

    # Log startup message
    log = structlog.get_logger("app.core.structlog_config")
    log.info(
        "Logging system initialized",
        log_level=log_level,
        json_format=settings.LOG_RENDER_JSON,
        environment=settings.ENVIRONMENT,
    )


def _configure_library_loggers(app_level: int) -> None:
    """
    Configure third-party library loggers to reduce noise and prevent raw exception output.

    This sets appropriate log levels for uvicorn, sqlalchemy, etc.
    to prevent duplicate or overly verbose logging.
    """
    # Logger configurations: (name, level, propagate)
    # Use CRITICAL to effectively disable, WARNING to reduce noise
    # Set propagate=False for loggers that have their own handlers to avoid duplication
    logger_configs = [
        # Uvicorn - completely disable to prevent raw exception tracebacks
        # Our error handlers will log exceptions in structured format
        ("uvicorn", logging.CRITICAL, False),
        ("uvicorn.error", logging.CRITICAL, False),
        ("uvicorn.access", logging.CRITICAL, False),
        # SQLAlchemy - only warnings and errors (reduce query noise)
        ("sqlalchemy", logging.WARNING, True),
        ("sqlalchemy.engine", logging.WARNING, True),
        ("sqlalchemy.engine.Engine", logging.WARNING, True),
        ("sqlalchemy.pool", logging.WARNING, True),
        ("sqlalchemy.dialects", logging.WARNING, True),
        ("sqlalchemy.orm", logging.WARNING, True),
        # Other libraries
        ("fastapi", logging.WARNING, True),
        ("starlette", logging.WARNING, True),
        ("alembic", logging.INFO, True),
        ("asyncio", logging.WARNING, True),
        ("watchfiles", logging.WARNING, True),  # Used by uvicorn --reload
        ("httpcore", logging.WARNING, True),
        ("httpx", logging.WARNING, True),
        ("aiosmtplib", logging.WARNING, True),
        # Gunicorn - show startup but not access logs
        ("gunicorn", logging.INFO, False),
        ("gunicorn.error", logging.INFO, False),
        ("gunicorn.access", logging.CRITICAL, False),
    ]

    for logger_name, level, propagate in logger_configs:
        lib_logger = logging.getLogger(logger_name)
        lib_logger.setLevel(level)
        lib_logger.propagate = propagate
        # Clear any existing handlers to prevent duplicate logs and raw output
        lib_logger.handlers.clear()


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """
    Get a structlog logger instance.

    This is the recommended way to get a logger throughout the application.

    Args:
        name: Logger name (typically __name__). If None, uses the caller's module.

    Returns:
        A bound structlog logger.

    Example:
        log = get_logger(__name__)
        log.info("User logged in", user_id="123")
    """
    return structlog.get_logger(name)


# Re-export for convenience
__all__ = [
    "get_logger",
    "get_request_id",
    "get_user_id",
    "set_user_id",
    "clear_user_id",
    "setup_logging",
]
