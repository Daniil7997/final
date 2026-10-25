from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status

from app.dependencies.admin import admin_service
from app.dependencies.auth import required_admin
from app.schemas.admin import (
    ChangeTeamMemberRole,
    CreateTeamRequest,
    CreateTeamResponse,
)
from app.schemas.common import SuccessMessageResponse
from app.schemas.types import IdType
from app.services.admin import AdminService

router = APIRouter(prefix='/admin', tags=["Administration"])


@router.post('/teams',
             status_code=status.HTTP_201_CREATED,
             response_model=CreateTeamResponse)
async def create_team(
    is_admin: Annotated[bool, Depends(required_admin)],
    data: Annotated[CreateTeamRequest, Body()],
    service: Annotated[AdminService, Depends(admin_service)]
) -> CreateTeamResponse:
    return await service.create_team(data=data)


@router.patch('/teams/{team_id}/members/{member_id}',
              status_code=status.HTTP_200_OK,
              response_model=SuccessMessageResponse)
async def change_team_member_role(
    is_admin: Annotated[bool, Depends(required_admin)],
    member_id: Annotated[IdType, Path()],
    team_id: Annotated[IdType, Path()],
    data: Annotated[ChangeTeamMemberRole, Body()],
    service: Annotated[AdminService, Depends(admin_service)]
) -> SuccessMessageResponse:
    await service.change_team_member_role(
        member_id=member_id,
        team_id=team_id,
        new_role=data.new_role
        )
    msg = (f"Team member with ID {member_id} successfully updated.")
    return SuccessMessageResponse(msg=msg)
