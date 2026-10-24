from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.domain.tasks.exceptions import TaskNotFoundError, TaskNotDoneError


def register_tasks_errors_handlers(app: FastAPI) -> None:

    @app.exception_handler(TaskNotFoundError)
    async def handle_task_not_found(
        request: Request,
        exc: TaskNotFoundError
    ) -> JSONResponse:
        msg = exc.msg or "Task not found"
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": msg}
        )

    @app.exception_handler(TaskNotDoneError)
    async def handle_task_not_done(
        request: Request,
        exc: TaskNotDoneError
    ) -> JSONResponse:
        msg = exc.msg or "Task not found"
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"msg": msg}
        )
