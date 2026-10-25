from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from app.core.exceptions.auth import (
    ForbiddenError,
    InvalidTokenTypeError,
    PasswordsDontMatchError,
    UnauthorizedError,
)


def register_auth_errors_handlers(app: FastAPI) -> None:

    @app.exception_handler(InvalidTokenError)
    async def handle_invalid_token(
        request: Request,
        exc: InvalidTokenError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"msg": "invalid token"},
            headers={"WWW-Authenticate": "Bearer"}
            )

    @app.exception_handler(ExpiredSignatureError)
    async def handle_expired_token(
        request: Request,
        exc: ExpiredSignatureError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"msg": "expired token"},
            headers={"WWW-Authenticate": "Bearer"}
            )

    @app.exception_handler(PasswordsDontMatchError)
    async def handle_passwords_dont_match(
        request: Request,
        exc: PasswordsDontMatchError
    ) -> JSONResponse:
        msg = exc.msg or "Passwords don't match"
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"msg": msg}
        )

    @app.exception_handler(ForbiddenError)
    async def handle_forbiden(
        request: Request,
        exc: ForbiddenError
    ) -> JSONResponse:
        msg = exc.msg or "Insufficient permissions"
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"msg": msg}
        )

    @app.exception_handler(InvalidTokenTypeError)
    async def handle_invalid_token_type(
        request: Request,
        exc: InvalidTokenTypeError
    ) -> JSONResponse:
        msg = exc.msg or "Invalid token type"
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"msg": msg},
            headers={"WWW-Authenticate": "Bearer"}
        )

    @app.exception_handler(UnauthorizedError)
    async def handle_unauthorized(
        request: Request,
        exc: UnauthorizedError
    ) -> JSONResponse:
        msg = exc.msg or "Authorization is required."
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"msg": msg},
            headers={"WWW-Authenticate": "Bearer"}
        )
