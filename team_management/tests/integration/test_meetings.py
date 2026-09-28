from datetime import timedelta, datetime

import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.users import Users
from app.models.teams import Teams
from app.schemas.auth import Tokens
from app.models.meetings import Meetings, MeetingsParticipants


class TestCreateMeeting:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_meeting(self,
                                  async_client: AsyncClient,
                                  api_prefix: str,
                                  manager_tokens: Tokens,
                                  team: Teams,
                                  test_session: AsyncSession):
        stmt = (select(Meetings)
                .where(Meetings.team_id == team.id))
        db_meeting = await test_session.scalar(stmt)
        assert db_meeting is None

        start_meeting = datetime.now() + timedelta(days=1, hours=2)
        end_meeting = start_meeting + timedelta(hours=1)
        description = "do something"

        response = await async_client.post(
            url=f'{api_prefix}/teams/{team.id}/meetings',
            json={
                "description": description,
                "start_meeting": start_meeting.isoformat(),
                "end_meeting": end_meeting.isoformat()
            },
            headers={"Authorization": f"Bearer {manager_tokens.access}"}
        )
        assert response.status_code == status.HTTP_201_CREATED

        db_meeting = await test_session.scalar(stmt)
        assert db_meeting is not None
        assert db_meeting.start_meeting == start_meeting
        assert db_meeting.end_meeting == end_meeting
        assert db_meeting.team_id == team.id

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_meeting_invalid_range(
        self,
        async_client: AsyncClient,
        api_prefix: str,
        manager_tokens: Tokens,
        team: Teams,
        test_session: AsyncSession
    ):
        stmt = (select(Meetings)
                .where(Meetings.team_id == team.id))
        db_meeting = await test_session.scalar(stmt)
        assert db_meeting is None

        start_meeting = datetime.now() + timedelta(days=1, hours=2)
        end_meeting = start_meeting - timedelta(hours=1)
        description = "do something"

        response = await async_client.post(
            url=f'{api_prefix}/teams/{team.id}/meetings',
            json={
                "description": description,
                "start_meeting": start_meeting.isoformat(),
                "end_meeting": end_meeting.isoformat()
            },
            headers={"Authorization": f"Bearer {manager_tokens.access}"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestAddUserToMeeting:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_add_user_to_meeting(
        self,
        async_client: AsyncClient,
        api_prefix: str,
        manager_tokens: Tokens,
        team: Teams,
        user_member: Users,
        meeting: Meetings,
        user_team_member: None,
        test_session: AsyncSession
    ):
        stmt = (select(MeetingsParticipants)
                .where(MeetingsParticipants.meeting_id == meeting.id,
                       MeetingsParticipants.user_id == user_member.id))
        db_meeting_user = await test_session.scalar(stmt)
        assert db_meeting_user is None

        response = await async_client.post(
            url=f'{api_prefix}/teams/{team.id}/meetings/{meeting.id}',
            json={
                "user_id": str(user_member.id),
            },
            headers={"Authorization": f"Bearer {manager_tokens.access}"}
        )
        assert response.status_code == status.HTTP_201_CREATED

        db_meeting_user = await test_session.scalar(stmt)
        assert db_meeting_user is not None


class TestGetMeetings:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_meetings(
        self,
        async_client: AsyncClient,
        api_prefix: str,
        manager_tokens: Tokens,
        team: Teams,
        meeting: Meetings,
    ):
        response = await async_client.get(
            url=f'{api_prefix}/teams/{team.id}/meetings',
            headers={"Authorization": f"Bearer {manager_tokens.access}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        obj = data[0]
        assert str(obj['id']) == str(meeting.id)
        assert obj['description'] == meeting.description
        assert obj['start_meeting'] == meeting.start_meeting.isoformat()
        assert obj['end_meeting'] == meeting.end_meeting.isoformat()


class TestDeleteMeeting:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_delete_meeting(
        self,
        async_client: AsyncClient,
        api_prefix: str,
        manager_tokens: Tokens,
        team: Teams,
        meeting: Meetings,
        test_session: AsyncSession
    ):
        stmt = (select(Meetings)
                .where(Meetings.id == meeting.id))
        db_meeting = await test_session.scalar(stmt)
        assert db_meeting is not None

        response = await async_client.delete(
            url=f'{api_prefix}/teams/{team.id}/meetings/{meeting.id}',
            headers={"Authorization": f"Bearer {manager_tokens.access}"}
        )
        assert response.status_code == status.HTTP_200_OK

        db_meeting_after_del = await test_session.scalar(stmt)
        assert db_meeting_after_del is None
