import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("finora.api")


def _request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


def _error_code(status_code: int) -> str:
    if status_code == status.HTTP_401_UNAUTHORIZED:
        return "authentication_error"
    if status_code == status.HTTP_403_FORBIDDEN:
        return "authorization_error"
    if status_code in {
        status.HTTP_400_BAD_REQUEST,
        status.HTTP_404_NOT_FOUND,
        status.HTTP_409_CONFLICT,
    }:
        return "business_error"
    return "http_error"


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "code": "validation_error",
                "detail": "Dados inválidos",
                "errors": [
                    {"location": error["loc"], "message": error["msg"], "type": error["type"]}
                    for error in exc.errors()
                ],
                "request_id": _request_id(request),
            },
        )

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": _error_code(exc.status_code),
                "detail": exc.detail,
                "request_id": _request_id(request),
            },
            headers=exc.headers,
        )

    @app.exception_handler(Exception)
    async def server_error(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(
            "unhandled_request_error",
            exc_info=exc,
            extra={"request_id": _request_id(request)},
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": "server_error",
                "detail": "Erro interno",
                "request_id": _request_id(request),
            },
        )
