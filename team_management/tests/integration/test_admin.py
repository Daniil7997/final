import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.infrastructure.db.models.teams import (
    TeamMembership,
    Teams,
    TeamsRoles,
)
from app.core.infrastructure.db.models.users import Users
from app.schemas.auth import Tokens


class TestCreateTeam:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_team(self,
                               async_client: AsyncClient,
                               api_prefix: str,
                               admin_tokens: Tokens,
                               user_no_team: Users):
        team_name = "best team"
        team_description = "some text"
        response = await async_client.post(
            url=f'{api_prefix}/admin/teams',
            json={
                "name": team_name,
                "description": team_description,
                "manager_id": str(user_no_team.id)
            },
            headers={"Authorization": f"Bearer {admin_tokens.access}"}
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['name'] == team_name
        assert data['description'] == team_description
        assert 'id' in response.json()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_team_no_permissions_actor_manager(
            self,
            async_client: AsyncClient,
            api_prefix: str,
            manager_tokens: Tokens
            ):
        body = {
            "name": "best team",
            "description": "some text",
        }
        response = await async_client.post(
            url=f'{api_prefix}/admin/teams',
            json=body,
            headers={"Authorization": f"Bearer {manager_tokens.access}"}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_team_no_permissions_actor_no_team(
            self,
            async_client: AsyncClient,
            api_prefix: str,
            user_no_team_tokens: Tokens
            ):
        body = {
            "name": "best team",
            "description": "some text",
        }
        response = await async_client.post(
            url=f'{api_prefix}/admin/teams',
            json=body,
            headers={"Authorization": f"Bearer {user_no_team_tokens.access}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestChangeTeamRole:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_change_team_role(self,
                                    async_client: AsyncClient,
                                    api_prefix: str,
                                    admin_tokens: Tokens,
                                    team: Teams,
                                    user_member: Users,
                                    test_session: AsyncSession):
        new_role = TeamsRoles.manager
        stmt = (select(TeamMembership.team_role)
                .where(TeamMembership.team_id == team.id,
                       TeamMembership.user_id == user_member.id))
        user_db_role = await test_session.scalar(stmt)
        assert user_db_role != new_role

        change_role_response = await async_client.patch(
            url=f'{api_prefix}/admin/teams/{team.id}/members/{user_member.id}',
            json={"new_role": new_role},
            headers={"Authorization": f"Bearer {admin_tokens.access}"}
        )
        assert change_role_response.status_code == status.HTTP_200_OK

        new_user_db_role = await test_session.scalar(stmt)
        assert new_user_db_role == new_role

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_change_team_role_no_permission_actor_manager(
            self,
            async_client: AsyncClient,
            api_prefix: str,
            manager_tokens: Tokens,
            team: Teams,
            user_member: Users,
            test_session: AsyncSession
            ):
        new_role = TeamsRoles.manager
        stmt = (select(TeamMembership.team_role)
                .where(TeamMembership.team_id == team.id,
                       TeamMembership.user_id == user_member.id))
        user_db_role = await test_session.scalar(stmt)
        assert user_db_role != new_role

        change_role_response = await async_client.patch(
            url=f'{api_prefix}/admin/teams/{team.id}/members/{user_member.id}',
            json={"new_role": new_role},
            headers={"Authorization": f"Bearer {manager_tokens.access}"}
        )
        assert change_role_response.status_code == status.HTTP_403_FORBIDDEN
        new_user_db_role = await test_session.scalar(stmt)
        assert new_user_db_role != new_role

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_change_team_role_no_permission_actor_no_team(
            self,
            async_client: AsyncClient,
            api_prefix: str,
            manager_tokens: Tokens,
            team: Teams,
            user_member: Users,
            test_session: AsyncSession
            ):
        new_role = TeamsRoles.manager
        stmt = (select(TeamMembership.team_role)
                .where(TeamMembership.team_id == team.id,
                       TeamMembership.user_id == user_member.id))
        user_db_role = await test_session.scalar(stmt)
        assert user_db_role != new_role

        change_role_response = await async_client.patch(
            url=f'{api_prefix}/admin/teams/{team.id}/members/{user_member.id}',
            json={"new_role": new_role},
            headers={"Authorization": f"Bearer {manager_tokens.access}"}
        )
        assert change_role_response.status_code == status.HTTP_403_FORBIDDEN
        new_user_db_role = await test_session.scalar(stmt)
        assert new_user_db_role != new_role