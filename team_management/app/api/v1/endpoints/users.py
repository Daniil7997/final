from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.dependencies.auth import id_from_access_token
from app.dependencies.users import users_service
from app.schemas.types import IdType
from app.schemas.users import GetProfileResponse
from app.services.users import UsersService

router = APIRouter(tags=["users"])


@router.get('/users/me',
            response_model=GetProfileResponse,
            status_code=status.HTTP_200_OK)
async def profile(
    id: Annotated[IdType, Depends(id_from_access_token)],
    service: Annotated[UsersService, Depends(users_service)]
) -> GetProfileResponse:
    return await service.profile_by_id(id=id)
