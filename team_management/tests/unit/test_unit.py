from datetime import UTC, datetime, timedelta

import pytest

from app.domain.meetings.exceptions import MeetingsOverlapError
from app.domain.meetings.rules import check_overlap
from app.schemas.structural import MeetingsSchema


class TestMeetingsOverlap:

    @pytest.mark.parametrize(
            "new_start, new_end",
            [
                (datetime.now(UTC),
                 datetime.now(UTC)+timedelta(minutes=30)),

                (datetime.now(UTC)+timedelta(hours=13),
                 datetime.now(UTC)+timedelta(hours=16)),
            ]
            )
    @pytest.mark.unit
    def test_check_overlap_positive(
            self,
            new_start: datetime,
            new_end: datetime,
            list_meetings_schema: list[MeetingsSchema]
            ):
        check_overlap(
            new_start=new_start,
            new_end=new_end,
            meetings=list_meetings_schema
        )


    @pytest.mark.parametrize(
            "new_start, new_end",
            [
                (datetime.now(UTC)+timedelta(hours=4),
                 datetime.now(UTC)+timedelta(hours=6)),

                (datetime.now(UTC)+timedelta(hours=3, minutes=30),
                 datetime.now(UTC)+timedelta(hours=6, minutes=30)),

                (datetime.now(UTC)+timedelta(hours=4, minutes=30),
                 datetime.now(UTC)+timedelta(hours=5, minutes=30)),

                (datetime.now(UTC)+timedelta(hours=3, minutes=30),
                 datetime.now(UTC)+timedelta(hours=4, minutes=30)),

                (datetime.now(UTC)+timedelta(hours=4, minutes=30),
                 datetime.now(UTC)+timedelta(hours=6, minutes=30)),
            ]
            )
    @pytest.mark.unit
    def test_check_overlap_negative(
            self,
            new_start: datetime,
            new_end: datetime,
            list_meetings_schema: list[MeetingsSchema]
            ):
        with pytest.raises(MeetingsOverlapError):
            check_overlap(
                new_start=new_start,
                new_end=new_end,
                meetings=list_meetings_schema
            )
