from datetime import timedelta, date

import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.users import Users
from app.models.teams import Teams
from app.models.tasks import Tasks, TaskStatus
from app.schemas.auth import Tokens
from app.models.evaluations import Evaluations


class TestCreateEvaluation:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_rate_task(
        self,
        async_client: AsyncClient,
        api_prefix: str,
        manager_tokens: Tokens,
        user_member: Users,
        team: Teams,
        task: Tasks,
        test_session: AsyncSession
    ):
        stmt_assignee = (update(Tasks)
                         .where(Tasks.id == task.id)
                         .values(assignee_id=user_member.id,
                                 status=TaskStatus.done))
        await test_session.execute(stmt_assignee)
        stmt_check_evaluation = (select(Evaluations)
                                 .where(Evaluations.task_id == task.id))
        db_evaluation = await test_session.scalar(stmt_check_evaluation)
        assert db_evaluation is None

        response = await async_client.post(
            url=f'{api_prefix}/teams/{team.id}/tasks/{task.id}/evaluations',
            json={
                "comment_text": "good job",
                "grade": 4,
            },
            headers={"Authorization": f"Bearer {manager_tokens.access}"}
        )
        assert response.status_code == status.HTTP_201_CREATED

        db_evaluation = await test_session.scalar(stmt_check_evaluation)
        assert db_evaluation is not None


class TestGetEvaluation:

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_rate_task(
        self,
        async_client: AsyncClient,
        api_prefix: str,
        member_tokens: Tokens,
        user_manager: Users,
        user_member: Users,
        team: Teams,
        test_session: AsyncSession
    ):
        due_date = date.today() + timedelta(days=2)

        task1 = Tasks(creator_id=user_manager.id,
                      due_date=due_date,
                      description='some_text',
                      team_id=team.id,
                      assignee_id=user_member.id,
                      status=TaskStatus.done)
        task2 = Tasks(creator_id=user_manager.id,
                      due_date=due_date,
                      description='some_text',
                      team_id=team.id,
                      assignee_id=user_member.id,
                      status=TaskStatus.done)
        task3 = Tasks(creator_id=user_manager.id,
                      due_date=due_date,
                      description='some_text',
                      team_id=team.id,
                      assignee_id=user_member.id,
                      status=TaskStatus.done)
        task4 = Tasks(creator_id=user_manager.id,
                      due_date=due_date,
                      description='some_text',
                      team_id=team.id,
                      assignee_id=user_member.id,
                      status=TaskStatus.done)
        task5 = Tasks(creator_id=user_manager.id,
                      due_date=due_date,
                      description='some_text',
                      team_id=team.id,
                      assignee_id=user_member.id,
                      status=TaskStatus.done)
        test_session.add_all([task1, task2, task3, task4, task5])
        await test_session.flush()

        evaluation1 = Evaluations(grade=1,
                                  task_id=task1.id,
                                  comment='bad',
                                  author_id=user_member.id,
                                  grader_id=user_manager.id)
        evaluation2 = Evaluations(grade=2,
                                  task_id=task2.id,
                                  author_id=user_member.id,
                                  grader_id=user_manager.id)
        evaluation3 = Evaluations(grade=3,
                                  task_id=task3.id,
                                  author_id=user_member.id,
                                  grader_id=user_manager.id)
        evaluation4 = Evaluations(grade=4,
                                  task_id=task4.id,
                                  author_id=user_member.id,
                                  grader_id=user_manager.id)
        evaluation5 = Evaluations(grade=5,
                                  task_id=task5.id,
                                  author_id=user_member.id,
                                  grader_id=user_manager.id)
        test_session.add_all([evaluation1, evaluation2, evaluation3,
                              evaluation4, evaluation5])
        await test_session.flush()
        grades = (evaluation1.grade,
                  evaluation2.grade,
                  evaluation3.grade,
                  evaluation4.grade,
                  evaluation5.grade)
        avg = sum(grades) / len(grades)
        expected = round(avg, 2)

        response = await async_client.get(
            url=f'{api_prefix}/users/me/evaluations',

            headers={"Authorization": f"Bearer {member_tokens.access}"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['average_evaluation'] == expected
