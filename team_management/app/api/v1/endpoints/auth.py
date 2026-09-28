from typing_extensions import Annotated

from fastapi import (Body,
                     Depends,
                     APIRouter,
                     status)

from app.schemas.auth import (RegisterUserRequest,
                              RegisterUserResponse,
                              TokensResponse,
                              TokensRequest,
                              ChangePasswordRequest)
from app.schemas.common import SuccessMessageResponse
from app.schemas.types import IdType
from app.services.auth import AuthService
from app.dependencies.auth import id_from_access_token, auth_service


router = APIRouter(tags=["auth"])


@router.post('/users',
             response_model=RegisterUserResponse,
             status_code=status.HTTP_201_CREATED)
async def register_user(
    data: Annotated[RegisterUserRequest, Body()],
    service: Annotated[AuthService, Depends(auth_service)]
) -> RegisterUserResponse:
    return await service.register_user(data=data)


@router.patch('/users/me/password',
              response_model=SuccessMessageResponse,
              status_code=status.HTTP_200_OK)
async def change_password(
    data: Annotated[ChangePasswordRequest, Body()],
    id: Annotated[IdType, Depends(id_from_access_token)],
    service: Annotated[AuthService, Depends(auth_service)]
) -> SuccessMessageResponse:
    await service.change_password(data=data, id=id)
    return SuccessMessageResponse(msg='Password successfully updated')


@router.post('/tokens',
             response_model=TokensResponse,
             status_code=status.HTTP_200_OK)
async def create_tokens(
    data: Annotated[TokensRequest, Body()],
    service: Annotated[AuthService, Depends(auth_service)]
) -> TokensResponse:
    return await service.get_tokens(data=data)
