import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.infrastructure.db.models.users import Users
from app.core.infrastructure.db.models.teams import Teams, TeamsRoles
from app.schemas.auth import Tokens
from app.core.infrastructure.storage.invite import invite_storage
from app.core.config import settings
from app.core.infrastructure.db.models.teams import TeamMembership


class TestCreateInvite:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_team_invite(self,
                                      async_client: AsyncClient,
                                      api_prefix: str,
                                      manager_tokens: Tokens,
                                      team: Teams):
        response = await async_client.post(
            url=f'{api_prefix}/teams/{team.id}/invites',
            headers={"Authorization": f"Bearer {manager_tokens.access}"}
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert 'invite_code' in data
        assert 'invite_code_ttl' in data
        response_invite_code = data['invite_code']
        storage_team_id = await invite_storage.get(response_invite_code)
        assert str(storage_team_id) == str(team.id)
        assert data['invite_code_ttl'] == settings.app.invite_code_ttl

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_team_no_permissions(
        self,
        async_client: AsyncClient,
        api_prefix: str,
        member_tokens: Tokens,
        team: Teams
    ):
        response = await async_client.post(
            url=f'{api_prefix}/teams/{team.id}/invites',
            headers={"Authorization": f"Bearer {member_tokens.access}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestJoinTeam:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_join_team(self,
                             async_client: AsyncClient,
                             api_prefix: str,
                             member_tokens: Tokens,
                             user_member: Users,
                             team_invite_code: str,
                             team: Teams):
        stmt = (select(TeamMembership)
                .where(TeamMembership.user_id==user_member.id,
                       TeamMembership.team_id==team.id))

        response = await async_client.post(
            url=f'{api_prefix}/teams/join',
            json={"invite_code": team_invite_code},
            headers={"Authorization": f"Bearer {member_tokens.access}"}
        )
        assert response.status_code == status.HTTP_200_OK
        members_response = await async_client.get(
            url=f'{api_prefix}/teams/{team.id}/members',
            headers={"Authorization": f"Bearer {member_tokens.access}"}
        )
        assert members_response.status_code == status.HTTP_200_OK
        data = members_response.json()
        team_member = next(x for x in data if x["email"] == user_member.email)
        assert team_member


class TestRemoveMember:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_remove_team_member(self,
                                      async_client: AsyncClient,
                                      api_prefix: str,
                                      manager_tokens: Tokens,
                                      member_tokens: Tokens,
                                      team: Teams,
                                      user_member: Users):

        members_response_before_rm = await async_client.get(
            url=f'{api_prefix}/teams/{team.id}/members',
            headers={"Authorization": f"Bearer {member_tokens.access}"}
        )
        assert members_response_before_rm.status_code == status.HTTP_200_OK

        rm_response = await async_client.delete(
            url=f'{api_prefix}/teams/{team.id}/members/{user_member.id}',
            headers={"Authorization": f"Bearer {manager_tokens.access}"}
        )
        assert rm_response.status_code == status.HTTP_200_OK

        members_response_after_rm = await async_client.get(
            url=f'{api_prefix}/teams/{team.id}/members',
            headers={"Authorization": f"Bearer {member_tokens.access}"}
        )
        assert (members_response_after_rm.status_code
                == status.HTTP_403_FORBIDDEN)


