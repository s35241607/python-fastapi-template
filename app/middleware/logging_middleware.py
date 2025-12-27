"""
Request logging middleware for FastAPI.

Provides:
- Correlation ID generation and propagation
- Request timing and access logging
- Context variable management for tracing
"""

from __future__ import annotations

import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import set_correlation_id, set_user_id


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that manages request context and access logging.

    Features:
    - Generates or inherits correlation ID from X-Correlation-ID header
    - Measures request duration
    - Logs access information (method, path, status, duration)
    - Injects correlation ID into response headers
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        # Get or generate correlation ID
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        set_correlation_id(correlation_id)

        # Try to get user ID from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            set_user_id(str(user_id))

        # Record start time
        start_time = time.perf_counter()

        # Process request
        response: Response
        try:
            response = await call_next(request)
        except Exception as e:
            # Calculate duration even on error
            duration_ms = (time.perf_counter() - start_time) * 1000
            # Use logger.opt(exception=True) for proper traceback formatting
            logger.opt(exception=True).error(
                f"Request failed: {request.method} {request.url.path} ({duration_ms:.1f}ms) - {type(e).__name__}: {e}",
            )
            raise

        # Calculate duration
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Log access
        log_message = f"{request.method} {request.url.path} {response.status_code} ({duration_ms:.1f}ms)"

        # Choose log level based on status code
        if response.status_code >= 500:
            logger.error(
                log_message,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
                client_ip=self._get_client_ip(request),
            )
        elif response.status_code >= 400:
            logger.warning(
                log_message,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
                client_ip=self._get_client_ip(request),
            )
        else:
            logger.info(
                log_message,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )

        # Add correlation ID to response headers for tracing
        response.headers["X-Correlation-ID"] = correlation_id

        return response

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request, considering proxy headers."""
        # Check for forwarded headers (common in reverse proxy setups)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP (original client)
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to direct client
        if request.client:
            return request.client.host

        return "unknown"
