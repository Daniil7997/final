import datetime as dt

from app.services.base import BaseService
from app.schemas.calendar import GetCalendarResponse
from app.schemas.types import IdType


class CalendarService(BaseService):

    async def get_user_calendar(
            self,
            actor_id: IdType,
            start: dt.datetime,
            end: dt.datetime):
        async with self.unit_of_work as uow:
            meetings = await uow.meetings.get_list_meetings_by_user_id(
                user_id=actor_id,
                start_meeting=start,
                end_meeting=end
                )
            tasks = await uow.tasks.get_list_tasks_by_user_id(
                user_id=actor_id,
                start=start.date(),
                end=end.date()
                )
            return GetCalendarResponse(tasks=tasks, meetings=meetings)
