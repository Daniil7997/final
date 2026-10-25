from typing import Annotated

from fastapi import Depends

from app.core.infrastructure.unit_of_work import UnitOfWork
from app.dependencies.db import get_unit_of_work
from app.services.tasks import TasksService


def tasks_service(
        unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)]
        ) -> TasksService:
    return TasksService(unit_of_work=unit_of_work)
