from typing import Annotated

from fastapi import Depends

from app.core.infrastructure.unit_of_work import UnitOfWork
from app.dependencies.db import get_unit_of_work
from app.services.teams import TeamsService


def teams_service(
        unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)]
        ) -> TeamsService:
    return TeamsService(unit_of_work=unit_of_work)
