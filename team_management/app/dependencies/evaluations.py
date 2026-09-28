from typing import Annotated

from fastapi import Depends

from app.core.infrastructure.unit_of_work import UnitOfWork
from app.services.evaluations import EvaluationsService
from app.dependencies.db import get_unit_of_work


def evaluations_service(
        unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)]
        ) -> EvaluationsService:
    return EvaluationsService(unit_of_work=unit_of_work)
