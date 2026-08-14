import json

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sentry_sdk import capture_exception
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.logger import client_errors_logger, logger


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(StarletteHTTPException)
    async def client_http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Обработчик клиентских ошибок"""

        if settings.LOGGING_CLIENT_ERRORS:
            request_data = {
                "method": request.method,
                "url": str(request.url),
                "client_ip": request.client.host,
                "headers": dict(request.headers),
                "body": None,
                "status_code": exc.status_code,
                "detail": exc.detail,
            }

            client_errors_logger.warning(json.dumps(request_data, ensure_ascii=False))

            capture_exception(exc, level="warning", extra=request_data)

        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Обработчик неожиданных ошибок"""

        logger.error(f"Unexpected error: {str(exc)}\n")

        capture_exception(exc)

        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
