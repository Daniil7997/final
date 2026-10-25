import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.infrastructure.db.models.teams import TeamMembership, Teams
from app.core.infrastructure.db.models.users import Users
from app.core.infrastructure.storage.invite import invite_storage
from app.core.security import create_tokens, hash_password
from app.schemas.auth import Tokens


class TestCreateInvite:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_team_invite(
            self,
            async_client: AsyncClient,
            api_prefix: str,
            manager_tokens: Tokens,
            team: Teams
            ):
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
    async def test_create_team_invite_actor_no_team(
            self,
            async_client: AsyncClient,
            api_prefix: str,
            user_no_team_tokens: Tokens,
            team: Teams
            ):
        response = await async_client.post(
            url=f'{api_prefix}/teams/{team.id}/invites',
            headers={"Authorization": f"Bearer {user_no_team_tokens.access}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestJoinTeam:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_join_team(self,
                             async_client: AsyncClient,
                             api_prefix: str,
                             team_invite_code: str,
                             team: Teams,
                             test_session: AsyncSession):

        user = Users(
            name='Artem',
            email='artem@example.com',
            password=hash_password(password='MyStrongPass'),
            is_admin=False,)
        test_session.add(user)
        await test_session.flush()
    
        user_tokens = create_tokens(user_id=user.id)
        
        check_stmt = (select(TeamMembership)
                      .where(TeamMembership.user_id==user.id,
                             TeamMembership.team_id==team.id))
        check_before_join = await test_session.scalar(check_stmt)
        assert check_before_join is None

        response = await async_client.post(
            url=f'{api_prefix}/teams/join',
            json={"invite_code": team_invite_code},
            headers={"Authorization": f"Bearer {user_tokens.access}"}
        )
        assert response.status_code == status.HTTP_200_OK

        check_after_join = await test_session.scalar(check_stmt)
        assert check_after_join is not None
        assert check_after_join.user_id == user.id
        assert check_after_join.team_id == team.id


class TestRemoveMember:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_remove_team_member(self,
                                      async_client: AsyncClient,
                                      api_prefix: str,
                                      manager_tokens: Tokens,
                                      team: Teams,
                                      user_member: Users,
                                      test_session: AsyncSession):
        check_stmt = (select(TeamMembership)
                      .where(TeamMembership.team_id==team.id,
                             TeamMembership.user_id==user_member.id))
        check_before_rm = await test_session.scalar(check_stmt)
        assert check_before_rm is not None
        assert check_before_rm.user_id == user_member.id
        assert check_before_rm.team_id == team.id

        rm_response = await async_client.delete(
            url=f'{api_prefix}/teams/{team.id}/members/{user_member.id}',
            headers={"Authorization": f"Bearer {manager_tokens.access}"}
        )
        assert rm_response.status_code == status.HTTP_200_OK

        check_after_rm = await test_session.scalar(check_stmt)
        assert check_after_rm is None

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_remove_team_member_actor_no_team(
            self,
            async_client: AsyncClient,
            api_prefix: str,
            user_no_team_tokens: Tokens,
            team: Teams,
            user_member: Users,
            test_session: AsyncSession
            ):
        check_stmt = (select(TeamMembership)
                      .where(TeamMembership.team_id==team.id,
                             TeamMembership.user_id==user_member.id))
        check_before_rm = await test_session.scalar(check_stmt)
        assert check_before_rm is not None
        assert check_before_rm.user_id == user_member.id
        assert check_before_rm.team_id == team.id

        rm_response = await async_client.delete(
            url=f'{api_prefix}/teams/{team.id}/members/{user_member.id}',
            headers={"Authorization": f"Bearer {user_no_team_tokens.access}"}
        )
        assert rm_response.status_code == status.HTTP_403_FORBIDDEN
