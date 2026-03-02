from typing import Any

import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

logger = structlog.get_logger("exceptions")


def _error_body(status: int, error: str, detail: Any = None) -> dict[str, Any]:
    return {"statusCode": status, "error": error, "detail": detail}


async def _http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(exc.status_code, type(exc).__name__, exc.detail),
    )


async def _validation_error_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=_error_body(422, "Validation Error", exc.errors()),
    )


async def _integrity_error_handler(_request: Request, exc: IntegrityError) -> JSONResponse:
    await logger.awarning("integrity_error", detail=str(exc.orig))
    return JSONResponse(
        status_code=409,
        content=_error_body(409, "Conflict", "A record with the given data already exists."),
    )


async def _unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    await logger.aerror("unhandled_error", exc_info=exc, request_id=request_id)
    return JSONResponse(
        status_code=500,
        content=_error_body(500, "Internal Server Error", "An unexpected error occurred."),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(HTTPException, _http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, _validation_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(IntegrityError, _integrity_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, _unhandled_error_handler)
