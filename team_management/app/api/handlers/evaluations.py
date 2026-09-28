from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.domain.evaluations.exceptions import EvaluationsNotFoundError


def register_evaluations_errors_handlers(app: FastAPI) -> None:

    @app.exception_handler(EvaluationsNotFoundError)
    async def handle_evaluations_not_found(
        request: Request,
        exc: EvaluationsNotFoundError
    ) -> JSONResponse:
        msg = exc.msg or "Evaluations not found"
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": msg}
        )
