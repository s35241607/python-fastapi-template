"""
Access logging middleware for FastAPI.

Provides:
- Request timing and access logging with structured output
- Exclusion of health check and monitoring endpoints
- Client IP detection (with proxy header support)
- User-Agent and request metadata logging
- Integration with structlog for consistent formatting

Note: request_id and user_id are automatically injected by the structlog
      processor chain (add_request_context), no need to add them manually.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from jose import jwt

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from app.core.structlog_config import clear_user_id, get_logger, set_user_id

log = get_logger(__name__)


class AccessLogMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs HTTP access with structured data.

    Features:
    - Logs method, path, status code, duration, client IP, user-agent
    - Excludes configurable paths (health checks, metrics, etc.)
    - Uses different log levels based on response status code
    - request_id and user_id are auto-injected by structlog processor
    """

    # Paths to exclude from access logging (health checks, monitoring)
    EXCLUDED_PATHS: set[str] = {
        "/health",
        "/healthz",
        "/ready",
        "/readyz",
        "/live",
        "/livez",
        "/metrics",
        "/favicon.ico",
    }

    # Path prefixes to exclude (OpenAPI docs in development)
    EXCLUDED_PREFIXES: tuple[str, ...] = (
        "/docs",
        "/redoc",
        "/openapi.json",
    )

    def __init__(self, app: ASGIApp, excluded_paths: set[str] | None = None) -> None:
        super().__init__(app)
        if excluded_paths:
            self.EXCLUDED_PATHS = self.EXCLUDED_PATHS | excluded_paths

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Response],
    ) -> Response:
        # Check if path should be excluded from logging
        path = request.url.path
        if self._should_exclude(path):
            return await call_next(request)

        # Optimistically extract user_id from token for logging context
        # This ensures we have user_id even if the request fails validation (422)
        # or auth dependency hasn't run yet.
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                token = auth_header.split(" ")[1]
                # Decode unverified to get subject for logging context only
                # The actual security check happens in the auth dependency
                payload = jwt.get_unverified_claims(token)
                user_id = payload.get("sub")
                if user_id:
                    set_user_id(str(user_id))
            except Exception:
                # Ignore extraction errors - let auth dependency handle 401 later
                pass

        # Record start time
        start_time = time.perf_counter()

        # Process request
        response: Response
        try:
            response = await call_next(request)
        except Exception:
            # Calculate duration even on error
            duration_ms = (time.perf_counter() - start_time) * 1000
            # Log the exception - request_id and user_id auto-injected by processor
            log.exception(
                "Request failed with unhandled exception",
                method=request.method,
                path=path,
                duration_ms=round(duration_ms, 2),
                client_ip=self._get_client_ip(request),
                user_agent=self._get_user_agent(request),
            )
            raise
        finally:
            # Clear user_id after request
            clear_user_id()

        # Calculate duration
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Prepare log data - request_id and user_id auto-injected by processor
        log_data: dict[str, Any] = {
            "method": request.method,
            "path": path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
            "client_ip": self._get_client_ip(request),
        }

        # Add additional context for non-2xx responses or slow requests
        if response.status_code >= 400 or duration_ms > 1000:
            log_data["user_agent"] = self._get_user_agent(request)
            log_data["query_string"] = str(request.query_params) if request.query_params else None
            log_data["content_type"] = request.headers.get("content-type")
            log_data["content_length"] = request.headers.get("content-length")
            log_data["referer"] = request.headers.get("referer")

        # Choose log level based on status code
        if response.status_code >= 500:
            log.error("access_log", **log_data)
        elif response.status_code >= 400:
            log.warning("access_log", **log_data)
        else:
            log.info("access_log", **log_data)

        return response

    def _should_exclude(self, path: str) -> bool:
        """Check if the path should be excluded from access logging."""
        if path in self.EXCLUDED_PATHS:
            return True
        return any(path.startswith(prefix) for prefix in self.EXCLUDED_PREFIXES)

    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP from request, considering proxy headers.

        Checks (in order):
        1. X-Forwarded-For (common in nginx/load balancers)
        2. X-Real-IP (nginx)
        3. CF-Connecting-IP (Cloudflare)
        4. Direct client IP
        """
        # X-Forwarded-For contains: client, proxy1, proxy2, ...
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP (original client)
            return forwarded_for.split(",")[0].strip()

        # X-Real-IP is set by nginx
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Cloudflare
        cf_ip = request.headers.get("cf-connecting-ip")
        if cf_ip:
            return cf_ip

        # Fall back to direct client
        if request.client:
            return request.client.host

        return "unknown"

    def _get_user_agent(self, request: Request) -> str:
        """Extract user-agent from request headers."""
        return request.headers.get("user-agent", "unknown")
