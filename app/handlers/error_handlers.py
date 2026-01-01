"""
Global exception handlers for the FastAPI application.

Provides:
- Consistent error response format across all exception types
- Structured logging with request context for debugging
- Safe request body preview (avoiding large files/binary content)
- Integration with structlog and asgi-correlation-id
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, cast

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.core.structlog_config import get_logger
from app.schemas.response import ErrorDetail, ErrorResponse

log = get_logger(__name__)


# Headers that should be filtered from logs (security)
SENSITIVE_HEADERS: set[str] = {
    "authorization",
    "cookie",
    "x-api-key",
    "x-auth-token",
    "x-csrf-token",
    "proxy-authorization",
}

# Content types that should not have body logged
BINARY_CONTENT_TYPES: tuple[str, ...] = (
    "multipart/form-data",
    "application/octet-stream",
    "image/",
    "video/",
    "audio/",
    "application/zip",
    "application/pdf",
    "application/gzip",
)


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers for the FastAPI application."""

    # Register most specific exceptions first
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)

    # Register the most general exception handler last
    app.add_exception_handler(Exception, unhandled_exception_handler)


async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle FastAPI validation errors with a consistent payload."""

    validation_error = cast(RequestValidationError, exc)

    errors: list[ErrorDetail] = []
    for error in validation_error.errors():
        field_path = [str(loc) for loc in error.get("loc", []) if str(loc) != "body"]
        field = ".".join(field_path) if field_path else "__root__"

        errors.append(
            ErrorDetail(
                field=field,
                message=error.get("msg", "Validation error."),
                type=error.get("type", "validation_error"),
            )
        )

    response = ErrorResponse(
        message="Validation Error",
        code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        errors=errors,
    )

    # Get body preview for debugging validation errors
    body_preview = await _safe_get_body_preview(request)

    # Log validation error with context (request_id/user_id auto-injected by processor)
    log.warning(
        "Validation error",
        method=request.method,
        path=str(request.url.path),
        error_count=len(errors),
        errors=[e.model_dump() for e in errors[:5]],  # Log first 5 errors
        request_body=body_preview,  # Include body for debugging
        content_type=request.headers.get("content-type"),
    )

    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=response.model_dump())


async def integrity_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle database integrity errors with appropriate HTTP status codes."""

    integrity_error = cast(IntegrityError, exc)

    # Check if it's a PostgreSQL error with error code
    error_code = None
    error_message = str(integrity_error)

    if hasattr(integrity_error, "orig") and integrity_error.orig and hasattr(integrity_error.orig, "pgcode"):
        error_code = getattr(integrity_error.orig, "pgcode", None)

    if error_code == "23505":  # unique_violation
        # Try to extract field name from error message
        field_name = "unknown"
        if "Key (" in error_message and ")=" in error_message:
            start = error_message.find("Key (") + 5
            end = error_message.find(")=", start)
            if end > start:
                field_name = error_message[start:end]

        response = ErrorResponse(
            message="Duplicate entry",
            code=status.HTTP_409_CONFLICT,
            errors=[
                ErrorDetail(
                    field=field_name,
                    message=f"A record with this {field_name} already exists.",
                    type="unique_constraint_violation",
                )
            ],
        )

        log.warning(
            "Unique constraint violation",
            method=request.method,
            path=str(request.url.path),
            field=field_name,
        )

        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content=response.model_dump())

    elif error_code == "23503":  # foreign_key_violation
        response = ErrorResponse(
            message="Foreign key constraint violation",
            code=status.HTTP_400_BAD_REQUEST,
            errors=[
                ErrorDetail(
                    field="__root__",
                    message="Cannot delete or update this record because it is referenced by other data.",
                    type="foreign_key_violation",
                )
            ],
        )

        log.warning(
            "Foreign key constraint violation",
            method=request.method,
            path=str(request.url.path),
        )

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=response.model_dump())

    elif error_code == "23502":  # not_null_violation
        # Try to extract column name
        column_name = "unknown"
        if "column" in error_message.lower():
            # Simple parsing - could be improved
            parts = error_message.split()
            for i, part in enumerate(parts):
                if part.lower() == "column":
                    column_name = parts[i + 1].strip('"') if i + 1 < len(parts) else "unknown"
                    break

        response = ErrorResponse(
            message="Required field missing",
            code=status.HTTP_400_BAD_REQUEST,
            errors=[
                ErrorDetail(
                    field=column_name,
                    message=f"The field '{column_name}' is required and cannot be null.",
                    type="not_null_violation",
                )
            ],
        )

        log.warning(
            "Not null constraint violation",
            method=request.method,
            path=str(request.url.path),
            column=column_name,
        )

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=response.model_dump())

    # For other integrity errors, treat as bad request
    response = ErrorResponse(
        message="Database constraint violation",
        code=status.HTTP_400_BAD_REQUEST,
        errors=[
            ErrorDetail(
                field="__root__",
                message="The operation violates database constraints.",
                type="integrity_error",
            )
        ],
    )

    log.warning(
        "Database integrity error",
        method=request.method,
        path=str(request.url.path),
        error_code=error_code,
    )

    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=response.model_dump())


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle HTTPException errors raised intentionally within the application."""

    # Handle both FastAPI and Starlette HTTPException
    if isinstance(exc, (HTTPException, StarletteHTTPException)):
        http_exc = cast(HTTPException, exc)

        message, errors = _prepare_http_exception_payload(http_exc.detail)

        response = ErrorResponse(
            message=message,
            code=http_exc.status_code,
            errors=errors,
        )

        # Log 4xx at warning level, 5xx at error level
        if http_exc.status_code >= 500:
            log.error(
                "HTTP exception",
                method=request.method,
                path=str(request.url.path),
                status_code=http_exc.status_code,
                message=message,
            )
        elif http_exc.status_code >= 400:
            log.warning(
                "HTTP exception",
                method=request.method,
                path=str(request.url.path),
                status_code=http_exc.status_code,
                message=message,
            )

        return JSONResponse(status_code=http_exc.status_code, content=response.model_dump())

    # Fallback for other exceptions (shouldn't happen but just in case)
    return await unhandled_exception_handler(request, exc)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle uncaught exceptions and ensure a consistent response payload."""

    # Safely get request body preview
    body_preview = await _safe_get_body_preview(request)

    # Filter sensitive headers
    safe_headers = _filter_sensitive_headers(dict(request.headers))

    # Log the full exception details for debugging
    log.exception(
        "Unhandled exception",
        method=request.method,
        path=str(request.url),
        query_params=dict(request.query_params),
        request_body=body_preview,
        headers=safe_headers,
        client_ip=_get_client_ip(request),
        exception_type=type(exc).__name__,
    )

    # In production, don't expose internal error details
    error_message = str(exc) if settings.DEBUG else "An internal error occurred"

    response = ErrorResponse(
        message="Internal Server Error",
        code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        errors=[
            ErrorDetail(
                field="__root__",
                message=error_message,
                type=exc.__class__.__name__,
            )
        ],
    )

    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=response.model_dump())


async def _safe_get_body_preview(request: Request, max_bytes: int = 2048) -> str | None:
    """
    Safely get a preview of the request body.

    This function:
    - Skips binary content types (file uploads, images, etc.)
    - Limits the size to prevent memory issues
    - Handles encoding errors gracefully
    - Returns a descriptive message for skipped content

    Args:
        request: The request object
        max_bytes: Maximum number of bytes to read (default 2KB)

    Returns:
        A string preview of the body, or a descriptive skip message
    """
    content_type = request.headers.get("content-type", "")

    # Skip binary content types
    for binary_type in BINARY_CONTENT_TYPES:
        if binary_type in content_type.lower():
            return f"[skipped: {content_type}]"

    # Check content length to avoid reading huge bodies
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            length = int(content_length)
            if length > max_bytes * 2:  # Allow some buffer
                return f"[skipped: body too large ({length} bytes)]"
        except ValueError:
            pass

    try:
        # Read the body (this consumes the stream, but for error logging it's acceptable)
        body = await request.body()

        if not body:
            return None

        if len(body) > max_bytes:
            return body[:max_bytes].decode("utf-8", errors="replace") + f"...[truncated, total {len(body)} bytes]"

        return body.decode("utf-8", errors="replace")

    except Exception as e:
        return f"[failed to read body: {type(e).__name__}]"


def _filter_sensitive_headers(headers: dict[str, str]) -> dict[str, str]:
    """
    Filter out sensitive headers from the dictionary.

    Replaces sensitive values with '[REDACTED]' to prevent
    accidental credential leakage in logs.
    """
    return {
        key: "[REDACTED]" if key.lower() in SENSITIVE_HEADERS else value
        for key, value in headers.items()
    }


def _get_client_ip(request: Request) -> str:
    """Extract client IP from request, considering proxy headers."""
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip

    if request.client:
        return request.client.host

    return "unknown"


def _prepare_http_exception_payload(detail: Any) -> tuple[str, list[ErrorDetail]]:
    """Normalise HTTPException detail into message and error detail list."""

    if isinstance(detail, str):
        return detail, []

    if isinstance(detail, dict):
        detail_mapping = cast(Mapping[Any, Any], detail)
        errors = [
            ErrorDetail(field=str(key), message=str(value), type="http_exception_detail")
            for key, value in detail_mapping.items()
        ]
        return "Application error", errors

    if isinstance(detail, list):
        detail_sequence = cast(Sequence[Any], detail)
        aggregated_errors: list[ErrorDetail] = []
        for index, item in enumerate(detail_sequence):
            if isinstance(item, dict):
                item_dict = cast(dict[str, Any], item)
                field = str(item_dict.get("field", index))
                message = str(item_dict.get("message", item))
                error_type = str(item_dict.get("type", "http_exception_detail"))
            else:
                field = str(index)
                message = str(item)
                error_type = "http_exception_detail"
            aggregated_errors.append(ErrorDetail(field=field, message=message, type=error_type))
        return "Application error", aggregated_errors

    # Fallback for unexpected detail types
    return str(detail), []
