from datetime import datetime

from app.domain.meetings.exceptions import MeetingsOverlapError
from app.schemas.structural import MeetingsSchema


def check_overlap(
        new_start: datetime,
        new_end: datetime,
        meetings: list[MeetingsSchema]
        ) -> None:
    for meeting in meetings:
        if (new_start < meeting.end_meeting
            and new_end > meeting.start_meeting):
            raise MeetingsOverlapError()
