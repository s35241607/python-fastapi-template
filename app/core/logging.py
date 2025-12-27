"""
Enterprise-grade logging configuration using Loguru.

This module provides:
- Unified logging for all application components (FastAPI, Uvicorn, SQLAlchemy)
- Structured JSON logging for production environments
- Colored console logging for development
- Log rotation, retention, and compression
- Request context injection (correlation_id)
- InterceptHandler to capture standard library logging
"""

from __future__ import annotations

import inspect
import logging
import sys
from contextvars import ContextVar
from pathlib import Path
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from loguru import Record

from app.config import settings

# Context variables for request tracing
correlation_id_var: ContextVar[str | None] = ContextVar("correlation_id", default=None)
user_id_var: ContextVar[str | None] = ContextVar("user_id", default=None)


class InterceptHandler(logging.Handler):
    """
    Intercept standard logging messages and redirect them to Loguru.

    This allows us to capture logs from third-party libraries like
    uvicorn, sqlalchemy, and fastapi, and route them through our
    unified Loguru configuration.
    """

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where the logged message originated
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def correlation_id_filter(record: Record) -> bool:
    """Add correlation_id to log records."""
    record["extra"]["correlation_id"] = correlation_id_var.get() or "-"
    record["extra"]["user_id"] = user_id_var.get() or "-"
    return True


def setup_logging() -> None:
    """
    Initialize the logging system with Loguru.

    This function should be called once at application startup,
    BEFORE any other imports that might use logging.

    IMPORTANT: This function aggressively removes all existing logging
    handlers to ensure unified output through Loguru.
    """
    # Remove default Loguru handler
    logger.remove()

    # Determine log level
    log_level = settings.LOG_LEVEL.upper()

    # Console handler configuration
    if settings.LOG_JSON_FORMAT:
        # JSON format for production (structured logging)
        logger.add(
            sys.stdout,
            level=log_level,
            format="{message}",
            serialize=True,  # Output as JSON
            filter=correlation_id_filter,
            enqueue=True,  # Thread-safe, async-safe
            backtrace=False,  # Don't include full traceback in JSON
            diagnose=False,  # Don't include variable values
        )
    else:
        # Human-readable format for development
        console_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{line}</cyan> | "
            "<dim>[{extra[correlation_id]}]</dim> "
            "<level>{message}</level>"
        )
        logger.add(
            sys.stdout,
            level=log_level,
            format=console_format,
            filter=correlation_id_filter,
            enqueue=True,
            backtrace=True,  # Include full traceback
            diagnose=False,  # Disable variable values to prevent truncation
            colorize=True,
        )

    # File handler with rotation (if path is specified)
    if settings.LOG_FILE_PATH:
        log_path = Path(settings.LOG_FILE_PATH)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            str(log_path),
            level=log_level,
            format="{message}",
            serialize=True,  # Always JSON for file logs
            filter=correlation_id_filter,
            enqueue=True,
            rotation=settings.LOG_ROTATION,  # e.g., "10 MB" or "00:00"
            retention=settings.LOG_RETENTION,  # e.g., "7 days"
            compression="gz",  # Compress rotated files
            encoding="utf-8",
        )

    # =========================================================================
    # INTERCEPT ALL STANDARD LIBRARY LOGGING
    # =========================================================================
    # Strategy:
    # 1. First, aggressively clear ALL handlers from ALL existing loggers
    # 2. Set up root logger with InterceptHandler
    # 3. Configure specific loggers with appropriate levels
    # =========================================================================

    # Step 1: Clear ALL handlers from ALL existing loggers
    # This is aggressive but necessary to prevent any duplicate output
    for name in logging.root.manager.loggerDict:
        logging.getLogger(name).handlers.clear()

    # Step 2: Configure root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(InterceptHandler())
    root_logger.setLevel(logging.DEBUG)

    # Step 3: Configure specific loggers with appropriate levels
    # All set propagate=False to avoid duplicate logs via root
    logger_levels = {
        # Uvicorn - keep error/startup logs, disable access (our middleware handles it)
        "uvicorn": logging.INFO,
        "uvicorn.error": logging.INFO,
        "uvicorn.access": logging.CRITICAL,  # Effectively disabled
        # SQLAlchemy - only warnings and above (reduce noise)
        "sqlalchemy": logging.WARNING,
        "sqlalchemy.engine": logging.WARNING,
        "sqlalchemy.engine.Engine": logging.WARNING,
        "sqlalchemy.pool": logging.WARNING,
        "sqlalchemy.dialects": logging.WARNING,
        "sqlalchemy.orm": logging.WARNING,
        # Others
        "fastapi": logging.INFO,
        "starlette": logging.INFO,
        "alembic": logging.INFO,
        "asyncio": logging.WARNING,
        "watchfiles": logging.WARNING,  # Used by uvicorn --reload
    }

    for logger_name, level in logger_levels.items():
        log = logging.getLogger(logger_name)
        log.handlers.clear()
        log.addHandler(InterceptHandler())
        log.setLevel(level)
        log.propagate = False

    logger.info(
        "Logging system initialized",
        log_level=log_level,
        json_format=settings.LOG_JSON_FORMAT,
        file_path=settings.LOG_FILE_PATH,
    )


def get_correlation_id() -> str | None:
    """Get the current correlation ID."""
    return correlation_id_var.get()


def set_correlation_id(correlation_id: str) -> None:
    """Set the correlation ID for the current context."""
    correlation_id_var.set(correlation_id)


def get_user_id() -> str | None:
    """Get the current user ID."""
    return user_id_var.get()


def set_user_id(user_id: str) -> None:
    """Set the user ID for the current context."""
    user_id_var.set(user_id)


# Re-export logger for convenience
__all__ = [
    "logger",
    "setup_logging",
    "get_correlation_id",
    "set_correlation_id",
    "get_user_id",
    "set_user_id",
]

