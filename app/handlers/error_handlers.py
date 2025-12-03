from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from typing import Any, cast

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.schemas.response import ErrorDetail, ErrorResponse

logger = logging.getLogger(__name__)


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

        return JSONResponse(status_code=http_exc.status_code, content=response.model_dump())

    # Fallback for other exceptions (shouldn't happen but just in case)
    return await unhandled_exception_handler(request, exc)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle uncaught exceptions and ensure a consistent response payload."""

    # Log the full exception details for debugging
    logger.error("Unhandled exception in %s %s", request.method, request.url.path, exc_info=exc)

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
