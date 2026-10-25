from datetime import timedelta, datetime, timezone

import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.infrastructure.db.models.users import Users
from app.core.infrastructure.db.models.teams import Teams
from app.schemas.auth import Tokens
from app.core.infrastructure.db.models.meetings import Meetings, MeetingsParticipants


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

        start_meeting = datetime.now(timezone.utc) + timedelta(days=1, hours=2)
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
    async def test_create_meeting_actor_no_team(
            self,
            async_client: AsyncClient,
            api_prefix: str,
            user_no_team_tokens: Tokens,
            team: Teams,
            test_session: AsyncSession
            ):
        stmt = (select(Meetings)
                .where(Meetings.team_id == team.id))
        db_meeting = await test_session.scalar(stmt)
        assert db_meeting is None

        start_meeting = datetime.now(timezone.utc) + timedelta(days=1, hours=2)
        end_meeting = start_meeting + timedelta(hours=1)
        description = "do something"

        response = await async_client.post(
            url=f'{api_prefix}/teams/{team.id}/meetings',
            json={
                "description": description,
                "start_meeting": start_meeting.isoformat(),
                "end_meeting": end_meeting.isoformat()
            },
            headers={"Authorization": f"Bearer {user_no_team_tokens.access}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

        db_meeting = await test_session.scalar(stmt)
        assert db_meeting is None

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

        start_meeting = datetime.now(timezone.utc) + timedelta(days=1, hours=2)
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

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_add_user_to_meeting_actor_no_team(
        self,
        async_client: AsyncClient,
        api_prefix: str,
        user_no_team_tokens: Tokens,
        team: Teams,
        user_member: Users,
        meeting: Meetings,
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
            headers={"Authorization": f"Bearer {user_no_team_tokens.access}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

        db_meeting_user = await test_session.scalar(stmt)
        assert db_meeting_user is None


    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_add_user_to_meeting_already_in_meeting(
        self,
        async_client: AsyncClient,
        api_prefix: str,
        manager_tokens: Tokens,
        team: Teams,
        user_member: Users,
        meeting: Meetings,
        test_session: AsyncSession
    ):
        add_user_to_meeting = MeetingsParticipants(
            user_id=user_member.id,
            meeting_id=meeting.id
        )
        test_session.add(add_user_to_meeting)
        await test_session.flush()
        stmt_check = (select(MeetingsParticipants)
                      .where(MeetingsParticipants.meeting_id == meeting.id,
                             MeetingsParticipants.user_id == user_member.id))
        db_meeting_user = await test_session.scalar(stmt_check)
        assert db_meeting_user is not None
        assert str(db_meeting_user.user_id) == str(user_member.id)

        response = await async_client.post(
            url=f'{api_prefix}/teams/{team.id}/meetings/{meeting.id}',
            json={
                "user_id": str(user_member.id),
            },
            headers={"Authorization": f"Bearer {manager_tokens.access}"}
        )
        assert response.status_code == status.HTTP_409_CONFLICT


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
        api_start_meeting = datetime.fromisoformat(obj['start_meeting'])
        api_end_meeting = datetime.fromisoformat(obj['end_meeting'])
        assert str(obj['id']) == str(meeting.id)
        assert obj['description'] == meeting.description
        assert api_start_meeting == meeting.start_meeting
        assert api_end_meeting == meeting.end_meeting

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_meetings_actor_no_team(
        self,
        async_client: AsyncClient,
        api_prefix: str,
        user_no_team_tokens: Tokens,
        team: Teams,
        meeting: Meetings,
    ):
        response = await async_client.get(
            url=f'{api_prefix}/teams/{team.id}/meetings',
            headers={"Authorization": f"Bearer {user_no_team_tokens.access}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


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

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_delete_meeting_actor_no_team(
        self,
        async_client: AsyncClient,
        api_prefix: str,
        user_no_team_tokens: Tokens,
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
            headers={"Authorization": f"Bearer {user_no_team_tokens.access}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

        db_meeting_after_del = await test_session.scalar(stmt)
        assert db_meeting_after_del is not None
