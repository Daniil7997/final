from typing import Annotated
from fastapi import Depends

from app.core.infrastructure.unit_of_work import UnitOfWork
from app.services.users import UsersService
from app.dependencies.db import get_unit_of_work


def users_service(
        unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)]
        ) -> UsersService:
    return UsersService(unit_of_work=unit_of_work)
