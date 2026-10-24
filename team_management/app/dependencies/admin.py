from typing import Annotated

from fastapi import Depends

from app.core.infrastructure.unit_of_work import UnitOfWork
from app.dependencies.db import get_unit_of_work
from app.services.admin import AdminService


def admin_service(
        unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)]
        ) -> AdminService:
    return AdminService(unit_of_work=unit_of_work)
