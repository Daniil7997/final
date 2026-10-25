from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status

from app.dependencies.auth import required_manager_or_higher
from app.dependencies.meetings import meetings_service
from app.schemas.common import SuccessMessageResponse
from app.schemas.meetings import (
    AddUserToMeetingRequest,
    CreateMeetingRequest,
    CreateMeetingsResponse,
    GetTeamMeetingsResponse,
)
from app.schemas.types import IdType, TeamsRoleType
from app.services.meetings import MeetingsService

router = APIRouter(tags=["meetings"])


@router.post('/teams/{team_id}/meetings',
             response_model=CreateMeetingsResponse,
             status_code=status.HTTP_201_CREATED)
async def create_meeting(
    actor_role: Annotated[TeamsRoleType, Depends(required_manager_or_higher)],
    team_id: Annotated[IdType, Path()],
    data: Annotated[CreateMeetingRequest, Body()],
    service: Annotated[MeetingsService, Depends(meetings_service)]
) -> CreateMeetingsResponse:
    return await service.create_meeting(data=data, team_id=team_id)


@router.post('/teams/{team_id}/meetings/{meeting_id}',
             response_model=SuccessMessageResponse,
             status_code=status.HTTP_201_CREATED)
async def add_user_to_meeting(
    actor_role: Annotated[TeamsRoleType, Depends(required_manager_or_higher)],
    team_id: Annotated[IdType, Path()],
    meeting_id: Annotated[IdType, Path()],
    data: Annotated[AddUserToMeetingRequest, Body()],
    service: Annotated[MeetingsService, Depends(meetings_service)]
) -> SuccessMessageResponse:
    await service.add_user_to_meeting(team_id=team_id,
                                      meeting_id=meeting_id,
                                      data=data)
    msg = "The user has been successfully added to the meeting."
    return SuccessMessageResponse(msg=msg)


@router.delete('/teams/{team_id}/meetings/{meeting_id}',
               response_model=SuccessMessageResponse,
               status_code=status.HTTP_200_OK)
async def delete_meeting(
    actor_role: Annotated[TeamsRoleType, Depends(required_manager_or_higher)],
    team_id: Annotated[IdType, Path()],
    meeting_id: Annotated[IdType, Path()],
    service: Annotated[MeetingsService, Depends(meetings_service)]
) -> SuccessMessageResponse:
    await service.delete_meeting(team_id=team_id, meeting_id=meeting_id)
    msg = "The meeting has been successfully deleted."
    return SuccessMessageResponse(msg=msg)


@router.get('/teams/{team_id}/meetings',
            response_model=list[GetTeamMeetingsResponse],
            status_code=status.HTTP_200_OK)
async def get_meetings(
    actor_role: Annotated[TeamsRoleType, Depends(required_manager_or_higher)],
    team_id: Annotated[IdType, Path()],
    service: Annotated[MeetingsService, Depends(meetings_service)]
) -> list[GetTeamMeetingsResponse]:
    return await service.get_team_meetings(team_id=team_id)
