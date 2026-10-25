import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.infrastructure.db.models.users import Users
from app.core.security import verify_password
from app.schemas.auth import Tokens


class TestRegisterUser:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_register_user(self,
                                 async_client: AsyncClient,
                                 api_prefix: str):
        response = await async_client.post(
            url=f'{api_prefix}/users',
            json={
                "name": "Ivan",
                "email": "ivan@gmail.com",
                "password": "secret1password"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Ivan"
        assert data["email"] == "ivan@gmail.com"
        assert "id" in data
        assert "password" not in data

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_register_user_conflict(self,
                                          async_client: AsyncClient,
                                          api_prefix: str,
                                          user_member: Users):
        conflict_response = await async_client.post(
            url=f'{api_prefix}/users',
            json={
                "name": user_member.name,
                "email": user_member.email,
                "password": user_member.password
            }
        )
        assert conflict_response.status_code == status.HTTP_409_CONFLICT


class TestChangePassword:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_change_password(self,
                                   async_client: AsyncClient,
                                   api_prefix: str,
                                   user_member: Users,
                                   member_tokens: Tokens,
                                   test_session: AsyncSession):

        old_password = user_member.password
        new_password = user_member.password + '1'

        change_password_response = await async_client.patch(
            url=f'{api_prefix}/users/me/password',
            json={
                "old_password": old_password,
                "new_password": new_password
            },
            headers={"Authorization": f"Bearer {member_tokens.access}"}
        )
        assert change_password_response.status_code == status.HTTP_200_OK
        stmt = (select(Users)
                .where(Users.id == user_member.id))
        result = await test_session.execute(stmt)
        db_user_data = result.scalar_one_or_none()
        assert db_user_data is not None
        check_old_password = verify_password(
            raw_password=old_password,
            hash_password=db_user_data.password
            )
        assert check_old_password is False
        check_new_password = verify_password(
            raw_password=new_password,
            hash_password=db_user_data.password
            )
        assert check_new_password is True


class TestTokens:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_tokens(self,
                          async_client: AsyncClient,
                          api_prefix: str,
                          user_member: Users):

        tokens_response = await async_client.post(
            url=f'{api_prefix}/tokens',
            json={
                "email": user_member.email,
                "password": user_member.password
            }
        )
        assert tokens_response.status_code == status.HTTP_200_OK
        tokens = tokens_response.json()
        assert 'access' in tokens

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_tokens_invalid_password(self,
                                           async_client: AsyncClient,
                                           api_prefix: str,
                                           user_member: Users):
        invalid_password = user_member.password + '1'

        tokens_response = await async_client.post(
            url=f'{api_prefix}/tokens',
            json={
                "email": user_member.email,
                "password": invalid_password
            }
        )
        assert tokens_response.status_code == status.HTTP_401_UNAUTHORIZED


class TestLogout:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_logout(
            self,
            async_client: AsyncClient,
            api_prefix: str,
            user_no_team_tokens: Tokens
            ):
        logout_response = await async_client.post(
            url=f'{api_prefix}/logout',
            headers={"Authorization": f"Bearer {user_no_team_tokens.access}"}
        )
        assert logout_response.status_code == status.HTTP_200_OK

        profile_response = await async_client.post(
            url=f'{api_prefix}/logout',
            headers={"Authorization": f"Bearer {user_no_team_tokens.access}"}
        )
        assert profile_response.status_code == status.HTTP_401_UNAUTHORIZED
