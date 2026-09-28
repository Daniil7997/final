from typing import Annotated

from fastapi import Depends

from app.core.infrastructure.unit_of_work import UnitOfWork
from app.services.calendar import CalendarService
from app.dependencies.db import get_unit_of_work


def calendar_service(
        unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)]
        ) -> CalendarService:
    return CalendarService(unit_of_work=unit_of_work)
