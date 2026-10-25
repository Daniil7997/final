from datetime import date, timedelta

import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.infrastructure.db.models.users import Users
from app.core.infrastructure.db.models.teams import Teams
from app.core.infrastructure.db.models.tasks import Tasks, TasksComments, TaskStatus
from app.schemas.auth import Tokens


class TestCreateTasks:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_tasks(self,
                                async_client: AsyncClient,
                                api_prefix: str,
                                manager_tokens: Tokens,
                                user_manager: Users,
                                team: Teams,
                                test_session: AsyncSession):
        due_date = date.today() + timedelta(days=3)
        description = "do something"

        response = await async_client.post(
            url=f'{api_prefix}/teams/{team.id}/tasks',
            json={
                "description": description,
                "due_date": due_date.isoformat()
            },
            headers={"Authorization": f"Bearer {manager_tokens.access}"}
        )
        assert response.status_code == status.HTTP_201_CREATED
        stmt = (select(Tasks)
                .where(Tasks.team_id == team.id))
        task = await test_session.scalar(stmt)
        assert task is not None
        assert task.creator_id == user_manager.id
        assert task.status == TaskStatus.open
        assert task.description == description
        assert task.due_date == due_date
        assert task.assignee_id is None

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_tasks_actor_no_team(
            self,
            async_client: AsyncClient,
            api_prefix: str,
            user_no_team_tokens: Tokens,
            team: Teams,
            test_session: AsyncSession
            ):
        due_date = date.today() + timedelta(days=3)
        description = "do something"

        response = await async_client.post(
            url=f'{api_prefix}/teams/{team.id}/tasks',
            json={
                "description": description,
                "due_date": due_date.isoformat()
            },
            headers={"Authorization": f"Bearer {user_no_team_tokens.access}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        stmt = (select(Tasks)
                .where(Tasks.team_id == team.id))
        task = await test_session.scalar(stmt)
        assert task is None


class TestDeleteTasks:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_delete_tasks(self,
                                async_client: AsyncClient,
                                api_prefix: str,
                                manager_tokens: Tokens,
                                team: Teams,
                                task: Tasks,
                                test_session: AsyncSession):
        stmt = (select(Tasks)
                .where(Tasks.id == task.id))
        db_task = await test_session.scalar(stmt)
        assert db_task is not None

        response = await async_client.delete(
            url=f'{api_prefix}/teams/{team.id}/tasks/{task.id}',
            headers={"Authorization": f"Bearer {manager_tokens.access}"}
        )
        assert response.status_code == status.HTTP_200_OK
        db_task = await test_session.scalar(stmt)
        assert db_task is None

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_delete_tasks_actor_no_team(
            self,
            async_client: AsyncClient,
            api_prefix: str,
            user_no_team_tokens: Tokens,
            team: Teams,
            task: Tasks,
            test_session: AsyncSession
            ):
        stmt = (select(Tasks)
                .where(Tasks.id == task.id))
        db_task = await test_session.scalar(stmt)
        assert db_task is not None

        response = await async_client.delete(
            url=f'{api_prefix}/teams/{team.id}/tasks/{task.id}',
            headers={"Authorization": f"Bearer {user_no_team_tokens.access}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        db_task = await test_session.scalar(stmt)
        assert db_task is not None


class TestUpdateTasks:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_update_tasks(self,
                                async_client: AsyncClient,
                                api_prefix: str,
                                manager_tokens: Tokens,
                                team: Teams,
                                task: Tasks,
                                test_session: AsyncSession):
        new_due_date = date.today() + timedelta(days=15)
        new_description = "A specific test description of the task."
        stmt = (select(Tasks)
                .where(Tasks.id == task.id))
        db_task = await test_session.scalar(stmt)
        assert db_task is not None
        assert db_task.due_date != new_due_date
        assert db_task.description != new_description

        response = await async_client.put(
            url=f'{api_prefix}/teams/{team.id}/tasks/{task.id}',
            json={"description": new_description,
                  "due_date": new_due_date.isoformat()},
            headers={"Authorization": f"Bearer {manager_tokens.access}"}
        )
        assert response.status_code == status.HTTP_200_OK

        db_task = await test_session.scalar(stmt)
        assert db_task is not None
        assert db_task.due_date == new_due_date
        assert db_task.description == new_description

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_update_tasks_actor_no_team(
            self,
            async_client: AsyncClient,
            api_prefix: str,
            user_no_team_tokens: Tokens,
            team: Teams,
            task: Tasks,
            test_session: AsyncSession
            ):
        new_due_date = date.today() + timedelta(days=15)
        new_description = "A specific test description of the task."
        stmt = (select(Tasks)
                .where(Tasks.id == task.id))
        db_task = await test_session.scalar(stmt)
        assert db_task is not None
        assert db_task.due_date != new_due_date
        assert db_task.description != new_description

        response = await async_client.put(
            url=f'{api_prefix}/teams/{team.id}/tasks/{task.id}',
            json={"description": new_description,
                  "due_date": new_due_date.isoformat()},
            headers={"Authorization": f"Bearer {user_no_team_tokens.access}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

        db_task = await test_session.scalar(stmt)
        assert db_task is not None
        assert db_task.due_date != new_due_date
        assert db_task.description != new_description
        assert db_task.due_date == task.due_date
        assert db_task.description == task.description


class TestChangeStatusTasks:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_change_status_tasks(self,
                                       async_client: AsyncClient,
                                       api_prefix: str,
                                       manager_tokens: Tokens,
                                       team: Teams,
                                       task: Tasks,
                                       test_session: AsyncSession):
        stmt = (select(Tasks)
                .where(Tasks.id == task.id))
        db_task = await test_session.scalar(stmt)
        assert db_task is not None
        assert db_task.status != TaskStatus.done

        response = await async_client.patch(
            url=f'{api_prefix}/teams/{team.id}/tasks/{task.id}',
            json={"new_status": TaskStatus.done},
            headers={"Authorization": f"Bearer {manager_tokens.access}"}
        )
        assert response.status_code == status.HTTP_200_OK

        db_task = await test_session.scalar(stmt)
        assert db_task is not None
        assert db_task.status == TaskStatus.done

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_change_status_tasks_actor_no_team(
            self,
            async_client: AsyncClient,
            api_prefix: str,
            user_no_team_tokens: Tokens,
            team: Teams,
            task: Tasks,
            test_session: AsyncSession
            ):
        stmt = (select(Tasks)
                .where(Tasks.id == task.id))
        db_task = await test_session.scalar(stmt)
        assert db_task is not None
        assert db_task.status != TaskStatus.done

        response = await async_client.patch(
            url=f'{api_prefix}/teams/{team.id}/tasks/{task.id}',
            json={"new_status": TaskStatus.done},
            headers={"Authorization": f"Bearer {user_no_team_tokens.access}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

        db_task = await test_session.scalar(stmt)
        assert db_task is not None
        assert db_task.status != TaskStatus.done


class TestCreateTaskComment:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_task_comment(self,
                                       async_client: AsyncClient,
                                       api_prefix: str,
                                       manager_tokens: Tokens,
                                       user_manager: Users,
                                       team: Teams,
                                       task: Tasks,
                                       test_session: AsyncSession):
        stmt = (select(TasksComments)
                .where(TasksComments.task_id == task.id))
        db_comment = await test_session.scalar(stmt)
        assert db_comment is None

        text_new_comment = "A substantial and important comment."
        response = await async_client.post(
            url=f'{api_prefix}/teams/{team.id}/tasks/{task.id}/comments',
            json={"comment_text": text_new_comment},
            headers={"Authorization": f"Bearer {manager_tokens.access}"}
        )
        assert response.status_code == status.HTTP_201_CREATED

        db_comment = await test_session.scalar(stmt)
        assert db_comment is not None
        assert db_comment.comment == text_new_comment
        assert db_comment.task_id == task.id
        assert db_comment.author_id == user_manager.id


class TestCreateTaskComment:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_task_comment_actor_no_team(
            self,
            async_client: AsyncClient,
            api_prefix: str,
            user_no_team_tokens: Tokens,
            team: Teams,
            task: Tasks,
            test_session: AsyncSession
            ):
        stmt = (select(TasksComments)
                .where(TasksComments.task_id == task.id))
        db_comment = await test_session.scalar(stmt)
        assert db_comment is None

        text_new_comment = "A substantial and important comment."
        response = await async_client.post(
            url=f'{api_prefix}/teams/{team.id}/tasks/{task.id}/comments',
            json={"comment_text": text_new_comment},
            headers={"Authorization": f"Bearer {user_no_team_tokens.access}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

        db_comment = await test_session.scalar(stmt)
        assert db_comment is None


class TestGetTask:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_task(
        self,
        async_client: AsyncClient,
        api_prefix: str,
        member_tokens: Tokens,
        team: Teams,
        task: Tasks
    ):

        response = await async_client.get(
            url=f'{api_prefix}/teams/{team.id}/tasks/{task.id}',
            headers={"Authorization": f"Bearer {member_tokens.access}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert str(data['id']) == str(task.id)
        assert str(data['creator_id']) == str(task.creator_id)
        assert data['description'] == task.description
        assert data['due_date'] == task.due_date.isoformat()

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_task_actor_no_team(
        self,
        async_client: AsyncClient,
        api_prefix: str,
        user_no_team_tokens: Tokens,
        team: Teams,
        task: Tasks
    ):

        response = await async_client.get(
            url=f'{api_prefix}/teams/{team.id}/tasks/{task.id}',
            headers={"Authorization": f"Bearer {user_no_team_tokens.access}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
