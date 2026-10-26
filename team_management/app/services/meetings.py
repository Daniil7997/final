from sqlalchemy.exc import IntegrityError

from app.core.infrastructure.db.codes import DBIntegrityState
from app.domain.meetings.exceptions import (
    InvalidMeetingTimeRangeError,
    MeetingNotFoundError,
    MeetingsOverlapError,
    UserAlreadyInMeetingError,
)
from app.domain.meetings.rules import check_overlap
from app.domain.teams.exceptions import (
    TeamMembershipRequiredError,
    TeamNotFoundError,
)
from app.domain.users.exceptions import UserNotFoundError
from app.schemas.meetings import (
    AddUserToMeetingRequest,
    CreateMeetingRequest,
    CreateMeetingsResponse,
    GetTeamMeetingsResponse,
)
from app.schemas.types import IdType
from app.services.base import BaseService


class MeetingsService(BaseService):

    async def create_meeting(
            self,
            team_id: IdType,
            data: CreateMeetingRequest
            ) -> CreateMeetingsResponse:
        async with self.unit_of_work as uow:
            try:
                meeting_id = await uow.meetings.create_meeting(
                    description=data.description,
                    start_meeting=data.start_meeting,
                    end_meeting=data.end_meeting,
                    team_id=team_id
                )
            except IntegrityError as e:
                sqlstate = getattr(e.orig, 'sqlstate', None)

                if sqlstate == DBIntegrityState.FOREIGN_KEY_VIOLATION:
                    raise TeamNotFoundError()

                elif sqlstate == DBIntegrityState.CHECK_VIOLATION:
                    raise InvalidMeetingTimeRangeError()
            if data.users_id is None:
                return CreateMeetingsResponse(meeting_id=meeting_id)
            await uow.advisory_lock_from_list_uuid(data.users_id)
            user_in_team = await uow.teams.check_users_in_team(
                users_id=data.users_id,
                team_id=team_id,
                )
            if not user_in_team:
                raise TeamMembershipRequiredError()
            existed_meetings = await uow.meetings.get_users_meetings(
                users_id=data.users_id
                )
            check_overlap(
                new_start=data.start_meeting,
                new_end=data.end_meeting,
                meetings=existed_meetings
            )
            try:
                await uow.meetings.join_meeting(
                    user_id=data.users_id,
                    meeting_id=meeting_id
                    )
            except IntegrityError as e:
                sqlstate = getattr(e.orig, 'sqlstate', None)

                if sqlstate == DBIntegrityState.FOREIGN_KEY_VIOLATION:
                    raise UserNotFoundError()

                elif sqlstate == DBIntegrityState.CHECK_VIOLATION:
                    raise MeetingsOverlapError()

            return CreateMeetingsResponse(meeting_id=meeting_id)

    async def add_user_to_meeting(
            self,
            team_id: IdType,
            meeting_id: IdType,
            data: AddUserToMeetingRequest,
    ) -> None:
        async with self.unit_of_work as uow:
            await uow.advisory_lock_from_list_uuid(data.users_id)
            user_in_team = await uow.teams.check_users_in_team(
                users_id=data.users_id,
                team_id=team_id,
                )
            if not user_in_team:
                raise TeamMembershipRequiredError()
            meeting_data = await uow.meetings.get_meeting_by_meeting_id(
                meeting_id=meeting_id
                )
            if meeting_data is None:
                raise MeetingNotFoundError()
            existed_meetings = await uow.meetings.get_users_meetings(
                users_id=data.users_id
                )
            check_overlap(
                new_start=meeting_data.start_meeting,
                new_end=meeting_data.end_meeting,
                meetings=existed_meetings
                )
            try:
                await uow.meetings.join_meeting(
                    user_id=data.users_id,
                    meeting_id=meeting_id
                    )
            except IntegrityError as e:
                sqlstate = getattr(e.orig, 'sqlstate', None)

                if sqlstate == DBIntegrityState.UNIQUE_VIOLATION:
                    raise UserAlreadyInMeetingError()

                elif sqlstate == DBIntegrityState.CHECK_VIOLATION:
                    raise MeetingsOverlapError()

    async def delete_meeting(self,
                             meeting_id: IdType,
                             team_id: IdType):
        async with self.unit_of_work as uow:
            await uow.meetings.delete_meeting(
                meeting_id=meeting_id,
                team_id=team_id
                )

    async def get_team_meetings(
            self,
            team_id: IdType
            ) -> list[GetTeamMeetingsResponse]:
        async with self.unit_of_work as uow:
            meetings = await uow.meetings.get_list_meetings_by_team_id(team_id)
            result = [GetTeamMeetingsResponse.model_validate(m.model_dump())
                      for m in meetings]
            return result
