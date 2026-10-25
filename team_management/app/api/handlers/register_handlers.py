from fastapi import FastAPI

from app.api.handlers.auth import register_auth_errors_handlers
from app.api.handlers.evaluations import register_evaluations_errors_handlers
from app.api.handlers.infrastructure import (
    register_infrastructure_errors_handlers,
)
from app.api.handlers.meetings import register_meetings_errors_handlers
from app.api.handlers.tasks import register_tasks_errors_handlers
from app.api.handlers.teams import register_teams_errors_handlers
from app.api.handlers.users import register_users_errors_handlers

handlers = [
    register_auth_errors_handlers,
    register_users_errors_handlers,
    register_teams_errors_handlers,
    register_tasks_errors_handlers,
    register_evaluations_errors_handlers,
    register_meetings_errors_handlers,
    register_infrastructure_errors_handlers
]


def register_all_handlers(app: FastAPI) -> None:
    for handler in handlers:
        handler(app)
