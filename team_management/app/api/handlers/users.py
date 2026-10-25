from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.domain.users.exceptions import (
    EmailAlreadyExistsError,
    UserNotFoundError,
)


def register_users_errors_handlers(app: FastAPI) -> None:

    @app.exception_handler(UserNotFoundError)
    async def handle_user_not_found(
        request: Request,
        exc: UserNotFoundError
    ):
        msg = exc.msg or "User not found"
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": msg})

    @app.exception_handler(EmailAlreadyExistsError)
    async def handle_email_already_exists(
            request: Request,
            exc: EmailAlreadyExistsError
    ):
        msg = exc.msg or "Email already exists"
        return JSONResponse(
              status_code=status.HTTP_409_CONFLICT,
              content={"msg": msg}
        )
