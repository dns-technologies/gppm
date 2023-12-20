from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException
from cryptography.fernet import InvalidToken
from typing import Awaitable, Callable, Any, Dict, Tuple
from functools import wraps

import app.use_case.exceptions as exce
from app.api.api_v1.api import api_router
from app.core.config import settings


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def json_response(
    func: Callable[..., Awaitable[Any]],
) -> Callable[..., Awaitable[JSONResponse]]:
    @wraps(func)
    async def with_logging(*args, **kwargs) -> JSONResponse:
        result = await func(*args, **kwargs)
        return JSONResponse(*result)

    return with_logging


@app.exception_handler(StarletteHTTPException)
@json_response
async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> Tuple[Dict, int]:
    return {"detail": exc.detail}, exc.status_code


@app.exception_handler(SQLAlchemyError)
@json_response
async def sqlalchemy_exception_handler(
    request: Request,
    exc: SQLAlchemyError,
) -> Tuple[Dict, int]:
    detail = "An unhandled exception occurred during a database query"
    return {"detail": detail}, 500


@app.exception_handler(InvalidToken)
@json_response
async def cryptography_exception_handler(
    request: Request,
    exc: InvalidToken,
) -> Tuple[Dict, int]:
    detail = "Incorrect ENCODING_KEY, data cannot be decrypted"
    return {"detail": detail}, 500


@app.exception_handler(exce.BaseUseCaseException)
@json_response
async def usecase_exception_handler(
    request: Request,
    exc: exce.BaseUseCaseException,
) -> Tuple[Dict, int]:
    errors_dict = {
        exce.NoSuchObject: f"Object not found: '{exc}'",
        exce.ObjectAlreadyExists: f"Object already exists: '{exc}'",
        exce.DoneWithErrors: f"Executed with errors: '{exc}'",
    }

    detail = errors_dict.get(type(exc), "Your request is invalid, please change it and try again")

    return {"detail": detail}, 400


app.include_router(api_router, prefix=settings.API_V1_STR)
