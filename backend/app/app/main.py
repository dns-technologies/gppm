from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware

from app.api.api_v1.api import api_router
import app.use_case.exceptions as exce
from app.core.config import settings
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException
from cryptography.fernet import InvalidToken
from loguru import logger
import sys

fmt = "[{level}] {message}"
config = {
    "handlers": [
        {"sink": sys.stderr, "format": fmt},
    ]
}
logger.configure(**config)

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def json_response(func):
    async def with_logging(*args, **kwargs):
        result = await func(*args, **kwargs)
        if settings.LOGGING_DEBUG:
            logger.debug(result)
        return JSONResponse(*result)

    return with_logging


@app.exception_handler(StarletteHTTPException)
@json_response
async def http_exception_handler(request: Request, exc: Exception):
    return {"detail": exc.detail}, exc.status_code


@app.exception_handler(SQLAlchemyError)
@json_response
async def sqlalchemy_exception_handler(request: Request, exc: Exception):
    detail = "An unhandled exception occurred during a database query"
    return {"detail": detail}, 500


@app.exception_handler(InvalidToken)
@json_response
async def cryptography_exception_handler(request: Request, exc: Exception):
    detail = "Incorrect ENCODING_KEY, data cannot be decrypted"
    return {"detail": detail}, 500


@app.exception_handler(exce.BaseUseCaseException)
@json_response
async def usecase_exception_handler(request: Request, exc: Exception):
    errors_dict = {
        exce.NoSuchObject: f"Object not found: '{exc}'",
        exce.ObjectAlreadyExists: f"Object already exists: '{exc}'",
        exce.DoneWithErrors: f"Executed with errors: '{exc}'",
    }

    detail = errors_dict.get(
        type(exc),
        "Your request is invalid, please change it and try again"
    )

    return {"detail": detail}, 400


app.include_router(api_router, prefix=settings.API_V1_STR)
