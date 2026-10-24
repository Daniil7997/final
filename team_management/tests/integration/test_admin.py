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


class TestCreateTeam:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_team(self,
                               async_client: AsyncClient,
                               api_prefix: str,
                               admin_tokens: Tokens,
                               user_member: Users):
        team_name = "best team"
        team_description = "some text"
        response = await async_client.post(
            url=f'{api_prefix}/admin/teams',
            json={
                "name": team_name,
                "description": team_description,
                "manager_id": str(user_member.id)
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
            url=f'{api_prefix}/admin/teams',
            json=body,
            headers={"Authorization": f"Bearer {member_tokens.access}"}
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
