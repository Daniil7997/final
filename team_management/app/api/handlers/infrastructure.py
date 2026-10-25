from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.infrastructure.exceptions import (
    InviteStorageNotConnectedError,
    InviteStorageUnavailableError,
    TokensBlacklistUnavailableError,
)


def register_infrastructure_errors_handlers(app: FastAPI) -> None:

    @app.exception_handler(InviteStorageUnavailableError)
    async def handle_invite_storage_unavailable(
        request: Request,
        exc: InviteStorageUnavailableError
    ) -> JSONResponse:
        msg = exc.msg or "Invite service is not available"
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"msg": msg},
            headers={"WWW-Authenticate": "Bearer"}
            )

    @app.exception_handler(InviteStorageNotConnectedError)
    async def handle_invite_storage_not_connected(
        request: Request,
        exc: InviteStorageNotConnectedError
    ) -> JSONResponse:
        msg = exc.msg or "Invite service is not connected"
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"msg": msg},
            headers={"WWW-Authenticate": "Bearer"}
            )

    @app.exception_handler(TokensBlacklistUnavailableError)
    async def handle_token_blacklist_unavailable(
        request: Request,
        exc: TokensBlacklistUnavailableError
    ) -> JSONResponse:
        msg = exc.msg or "Logout is unavailable due to technical reasons."
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"msg": msg},
            headers={"WWW-Authenticate": "Bearer"}
            )
