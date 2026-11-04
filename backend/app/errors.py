import logging

from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger("smart_budget_guard.errors")


def _error(status_code: int, detail: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": detail})


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        first = exc.errors()[0]
        field = ".".join(str(p) for p in first["loc"] if p != "body")
        prefix = f"{field}: " if field else ""
        return _error(422, f"Invalid request: {prefix}{first['msg']}")

    @app.exception_handler(ClientAuthenticationError)
    async def azure_auth_handler(request: Request, exc: ClientAuthenticationError):
        logger.error("Azure authentication failed on %s", request.url.path)
        return _error(
            502,
            "Azure authentication failed. Run 'az login' on the machine running the backend.",
        )

    @app.exception_handler(HttpResponseError)
    async def azure_http_handler(request: Request, exc: HttpResponseError):
        logger.error("Azure request failed on %s: %s", request.url.path, exc.message)
        return _error(502, "Azure request failed. See the backend logs for details.")

    @app.exception_handler(SQLAlchemyError)
    async def db_handler(request: Request, exc: SQLAlchemyError):
        logger.exception("Database error on %s", request.url.path)
        return _error(503, "Database error. Check that PostgreSQL is running.")

    # Catch-all for anything unexpected. This is middleware rather than an
    # Exception handler so the response still passes through CORS (see main.py).
    @app.middleware("http")
    async def catch_unhandled(request: Request, call_next):
        try:
            return await call_next(request)
        except Exception:
            logger.exception("Unhandled error on %s %s", request.method, request.url.path)
            return _error(500, "Unexpected server error. See the backend logs for details.")