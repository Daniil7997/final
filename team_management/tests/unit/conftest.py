import uuid
from datetime import UTC, datetime, timedelta

import pytest

from app.schemas.structural import MeetingsSchema


@pytest.fixture(scope='function')
def list_meetings_schema() -> list[MeetingsSchema]:
    now = datetime.now(UTC)
    one = MeetingsSchema(
        id=uuid.uuid7(),
        created_at=now,
        updated_at=now,
        description="some text",
        start_meeting=now+timedelta(hours=1),
        end_meeting=now+timedelta(hours=3),
        team_id=uuid.uuid7()
    )
    two = MeetingsSchema(
        id=uuid.uuid7(),
        created_at=now,
        updated_at=now,
        description="some text",
        start_meeting=now+timedelta(hours=4),
        end_meeting=now+timedelta(hours=6),
        team_id=uuid.uuid7()
    )
    three = MeetingsSchema(
        id=uuid.uuid7(),
        created_at=now,
        updated_at=now,
        description="some text",
        start_meeting=now+timedelta(hours=7),
        end_meeting=now+timedelta(hours=10),
        team_id=uuid.uuid7()
    )
    return [one, two, three]
