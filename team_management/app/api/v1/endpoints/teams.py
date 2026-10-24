from typing_extensions import Annotated

from fastapi import (Body,
                     Path,
                     Depends,
                     APIRouter,
                     status)

from app.schemas.teams import (CreateInviteResponse,
                               JoinTeamRequest,
                               GetMembershipResponse)
from app.schemas.types import IdType, TeamsRoleType
from app.schemas.common import SuccessMessageResponse
from app.dependencies.auth import (required_manager_or_higher,
                                   id_from_access_token)
from app.dependencies.teams import teams_service
from app.services.teams import TeamsService


router = APIRouter(tags=["teams"])


@router.post('/teams/{team_id}/invites',
             status_code=status.HTTP_201_CREATED,
             response_model=CreateInviteResponse)
async def create_invite_code(
    user_role: Annotated[TeamsRoleType, Depends(required_manager_or_higher)],
    team_id: Annotated[IdType, Path],
    user_id: Annotated[IdType, Depends(id_from_access_token)],
    service: Annotated[TeamsService, Depends(teams_service)]
) -> CreateInviteResponse:
    return await service.create_invite(user_id=user_id, team_id=team_id)


@router.post('/teams/join',
             status_code=status.HTTP_200_OK,
             response_model=SuccessMessageResponse)
async def join_team(
    user_id: Annotated[IdType, Depends(id_from_access_token)],
    data: Annotated[JoinTeamRequest, Body()],
    service: Annotated[TeamsService, Depends(teams_service)]
) -> SuccessMessageResponse:
    team_id = await service.join_team(data=data, user_id=user_id)
    msg = f"You have successfully joined team ID {team_id}."
    return SuccessMessageResponse(msg=msg)


@router.get('/teams/{team_id}/members',
            status_code=status.HTTP_200_OK,
            response_model=list[GetMembershipResponse])
async def team_members(
    actor_id: Annotated[IdType, Depends(id_from_access_token)],
    team_id: Annotated[IdType, Path()],
    service: Annotated[TeamsService, Depends(teams_service)]
) -> list[GetMembershipResponse]:
    return await service.get_team_membership(team_id=team_id,
                                             actor_id=actor_id)


@router.delete('/teams/{team_id}/members/{member_id}',
               status_code=status.HTTP_200_OK,
               response_model=SuccessMessageResponse)
async def remove_team_member(
    actor_role: Annotated[TeamsRoleType, Depends(required_manager_or_higher)],
    actor_id: Annotated[IdType, Depends(id_from_access_token)],
    member_id: Annotated[IdType, Path()],
    team_id: Annotated[IdType, Path()],
    service: Annotated[TeamsService, Depends(teams_service)]
) -> SuccessMessageResponse:
    removed_member_id = await service.remove_team_member(member_id=member_id,
                                                         actor_id=actor_id,
                                                         team_id=team_id)
    msg = (f"Team member with ID {removed_member_id} successfully removed.")
    return SuccessMessageResponse(msg=msg)
