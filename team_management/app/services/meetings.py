from sqlalchemy.exc import IntegrityError

from app.services.base import BaseService
from app.schemas.meetings import (CreateMeetingRequest,
                                  CreateMeetingsResponse,
                                  AddUserToMeetingRequest,
                                  GetTeamMeetingsResponse)
from app.schemas.types import IdType
from app.domain.teams.exceptions import (TeamMembershipRequiredError,
                                         TeamNotFoundError)
from app.domain.meetings.exceptions import (MeetingsOverlapError,
                                            InvalidMeetingTimeRangeError,
                                            MeetingNotFoundError,
                                            UserAlreadyInMeetingError)
from app.domain.users.exceptions import UserNotFoundError
from app.core.infrastructure.db.codes import DBIntegrityState


class MeetingsService(BaseService):

    async def create_meeting(
            self,
            actor_id: IdType,
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
            if data.user_id is None:
                return CreateMeetingsResponse(meeting_id=meeting_id)
            try:
                await uow.meetings.join_meeting(
                    user_id=data.user_id,
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
            lock_key = uow.key_factory.uuid_to_bigint(data.user_id)
            await uow.locker.lock(lock_key)
            user_in_team = await uow.teams.check_user_in_team(
                user_id=data.user_id,
                team_id=team_id,
            )
            if not user_in_team:
                raise TeamMembershipRequiredError()
            meeting_data = await uow.meetings.get_meeting_by_meeting_id(
                meeting_id=meeting_id
                )
            if meeting_data is None:
                raise MeetingNotFoundError()
            overlap = await uow.meetings.check_overlap_meetings(
                user_id=data.user_id,
                start_meeting=meeting_data.start_meeting,
                end_meeting=meeting_data.end_meeting)
            if overlap:
                raise MeetingsOverlapError()
            try:
                await uow.meetings.join_meeting(
                    user_id=data.user_id,
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
                             actor_id: IdType,
                             team_id: IdType):
        async with self.unit_of_work as uow:
            await uow.meetings.delete_meeting(
                meeting_id=meeting_id,
                team_id=team_id
                )

    async def get_team_meetings(
            self,
            team_id: IdType,
            actor_id: IdType) -> list[GetTeamMeetingsResponse]:
        async with self.unit_of_work as uow:
            actor_in_team = await uow.teams.check_user_in_team(user_id=actor_id,
                                                               team_id=team_id)
            if not actor_in_team:
                raise TeamMembershipRequiredError()
            meetings = await uow.meetings.get_list_meetings_by_team_id(team_id)
            result = [GetTeamMeetingsResponse.model_validate(m.model_dump())
                      for m in meetings]
            return result
