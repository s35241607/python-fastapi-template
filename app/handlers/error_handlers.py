from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from typing import Any, cast

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.schemas.response import ErrorDetail, ErrorResponse

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers for the FastAPI application."""

    # Register most specific exceptions first
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
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
    error_message = str(exc) if settings.debug else "An internal error occurred"

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
