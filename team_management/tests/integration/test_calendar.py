from datetime import UTC, date, datetime, timedelta

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.infrastructure.db.models.meetings import (
    Meetings,
    MeetingsParticipants,
)
from app.core.infrastructure.db.models.tasks import Tasks
from app.core.infrastructure.db.models.teams import Teams
from app.core.infrastructure.db.models.users import Users
from app.schemas.auth import Tokens
from app.schemas.structural import MeetingsSchema, TaskSchema


class TestGetCalendar:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_calendar(self,
                                async_client: AsyncClient,
                                api_prefix: str,
                                member_tokens: Tokens,
                                user_manager: Users,
                                user_member: Users,
                                team: Teams,
                                test_session: AsyncSession):
        due_date = date.today() + timedelta(days=2)
        task = Tasks(creator_id=user_manager.id,
                     due_date=due_date,
                     description='some_text',
                     team_id=team.id,
                     assignee_id=user_member.id)
        start_meeting = datetime.now(UTC) + timedelta(days=1, hours=2)
        end_meeting = start_meeting + timedelta(hours=1)
        meeting = Meetings(
            description="some text",
            start_meeting=start_meeting,
            end_meeting=end_meeting,
            team_id=team.id
        )
        test_session.add_all([task, meeting])
        await test_session.flush()
        user_in_meeting = MeetingsParticipants(user_id=user_member.id,
                                               meeting_id=meeting.id)
        test_session.add(user_in_meeting)
        await test_session.flush()

        start = datetime.now()
        end = start + timedelta(days=10)
        response = await async_client.get(
            url=f'{api_prefix}/calendar',
            params={
                "start": start.isoformat(),
                "end": end.isoformat()
                },
            headers={"Authorization": f"Bearer {member_tokens.access}"}
        )
        assert response.status_code == status.HTTP_200_OK
        tasks = response.json()['tasks']
        meetings = response.json()['meetings']
        assert isinstance(tasks, list)
        assert len(tasks) == 1
        assert isinstance(meetings, list)
        assert len(meetings) == 1
        valid_task = TaskSchema.model_validate(tasks[0])
        assert str(valid_task.id) == str(task.id)
        valid_meeting = MeetingsSchema.model_validate(meetings[0])
        assert str(valid_meeting.id) == str(meeting.id)
