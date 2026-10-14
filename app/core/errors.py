# Pocket Option Data Harvester — Core Errors & Error Handlers
from typing import Any
from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse


# ── Domain Exceptions ─────────────────────────────────────────────────────────

class AppError(Exception):
    """Base class for all application errors."""


class CollectorAlreadyRunning(AppError):
    """Raised when start() is called on an already running engine."""


class CollectorNotRunning(AppError):
    """Raised when pause/resume/stop is called when engine is stopped."""


class SessionRequired(AppError):
    """Raised when the collector needs a session token that is not configured."""


class DatabaseNotConnected(AppError):
    """Raised when a database operation is attempted before connecting."""


# ── Handler Factory ───────────────────────────────────────────────────────────

def _make_handler(status_code: int, detail: Any):
    async def handler(request: Request, exc: AppError):
        return JSONResponse(
            content={"status_code": status_code, "detail": detail},
            status_code=status_code,
        )
    return handler


# ── Registration ──────────────────────────────────────────────────────────────

def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        CollectorAlreadyRunning,
        _make_handler(
            status.HTTP_409_CONFLICT,
            {"message": "Collector is already running", "error_code": "collector_already_running"},
        ),
    )
    app.add_exception_handler(
        CollectorNotRunning,
        _make_handler(
            status.HTTP_409_CONFLICT,
            {"message": "Collector is not running", "error_code": "collector_not_running"},
        ),
    )
    app.add_exception_handler(
        SessionRequired,
        _make_handler(
            status.HTTP_400_BAD_REQUEST,
            {"message": "A valid session token is required to start the collector", "error_code": "session_required"},
        ),
    )
    app.add_exception_handler(
        DatabaseNotConnected,
        _make_handler(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            {"message": "Database is not connected", "error_code": "database_not_connected"},
        ),
    )

    # ── FastAPI validation errors → human-readable ────────────────────────────
    from fastapi.exceptions import RequestValidationError

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = []
        for error in exc.errors():
            loc = error.get("loc", ())
            field = str(loc[-1]) if loc else "unknown"
            msg = error.get("msg", "Invalid value")
            errors.append({"field": field, "message": msg, "error_code": "validation_error"})

        primary = errors[0] if errors else {"message": "Invalid input", "field": "unknown", "error_code": "validation_error"}
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "status_code": 422,
                "detail": {
                    "message": primary["message"],
                    "error_code": "validation_error",
                    "field": primary["field"],
                    "errors": errors,
                },
            },
        )

    @app.exception_handler(500)
    async def internal_server_error(request: Request, exc: Exception):
        import traceback
        traceback.print_exc()
        return JSONResponse(
            content={"message": "Internal server error", "error_code": "server_error"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
