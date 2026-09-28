import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.users import Users
from app.models.teams import Teams
from app.schemas.auth import Tokens
from app.core.infrastructure.storage.invite import invite_storage
from app.core.config import settings
from app.models.teams import TeamMembership


class TestCreateTeam:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_team(self,
                               async_client: AsyncClient,
                               api_prefix: str,
                               manager_tokens: Tokens):
        team_name = "best team"
        team_description = "some text"
        body = {
            "name": team_name,
            "description": team_description,
        }
        response = await async_client.post(
            url=f'{api_prefix}/teams',
            json=body,
            headers={"Authorization": f"Bearer {manager_tokens.access}"}
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['name'] == team_name
        assert data['description'] == team_description
        assert 'id' in response.json()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_team_no_permissions(self,
                                              async_client: AsyncClient,
                                              api_prefix: str,
                                              member_tokens: Tokens):
        team_name = "best team"
        team_description = "some text"
        body = {
            "name": team_name,
            "description": team_description,
        }
        response = await async_client.post(
            url=f'{api_prefix}/teams',
            json=body,
            headers={"Authorization": f"Bearer {member_tokens.access}"}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


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
                                      user_member: Users,
                                      user_team_member: None):

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


class TestChangeTeamRole:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_change_team_role(self,
                                    async_client: AsyncClient,
                                    api_prefix: str,
                                    manager_tokens: Tokens,
                                    team: Teams,
                                    user_member: Users,
                                    test_session: AsyncSession,
                                    user_team_member: None):
        my_custom_role = 'role transition marker'
        stmt = (select(TeamMembership.team_role)
                .where(TeamMembership.team_id == team.id,
                       TeamMembership.user_id == user_member.id))
        user_db_role = await test_session.scalar(stmt)
        assert user_db_role != my_custom_role

        change_role_response = await async_client.patch(
            url=f'{api_prefix}/teams/{team.id}/members/{user_member.id}',
            json={"new_role": my_custom_role},
            headers={"Authorization": f"Bearer {manager_tokens.access}"}
        )
        assert change_role_response.status_code == status.HTTP_200_OK

        new_user_db_role = await test_session.scalar(stmt)
        assert new_user_db_role == my_custom_role
