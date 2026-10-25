from typing import Annotated

from fastapi import APIRouter, Body, Depends, status

from app.dependencies.auth import (
    auth_service,
    id_from_access_token,
    str_token_from_header,
)
from app.schemas.auth import (
    ChangePasswordRequest,
    RegisterUserRequest,
    RegisterUserResponse,
    TokensRequest,
    TokensResponse,
)
from app.schemas.common import SuccessMessageResponse
from app.schemas.types import IdType
from app.services.auth import AuthService

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


@router.post('/logout',
             response_model=TokensResponse,
             status_code=status.HTTP_200_OK)
async def logout(
    token: Annotated[str, Depends(str_token_from_header)],
    id: Annotated[str, Depends(id_from_access_token)],
    service: Annotated[AuthService, Depends(auth_service)]
) -> SuccessMessageResponse:
    await service.logout(token=token, id=id)
    return SuccessMessageResponse(msg='Logout completed successfully')
