from app.core.infrastructure.db.models.tasks import TaskStatus
from app.schemas.structural import TaskSchema
from app.services.base import BaseService
from app.schemas.evaluations import (CreateEvaluationsRequest,
                                     GetAvgEvaluation)
from app.schemas.types import IdType
from app.domain.tasks.exceptions import TaskNotFoundError, TaskNotDoneError
from app.domain.evaluations.exceptions import EvaluationsNotFoundError


class EvaluationsService(BaseService):

    async def create_evaluation(self,
                                actor_id: IdType,
                                task_id: IdType,
                                team_id: IdType,
                                data: CreateEvaluationsRequest):
        async with self.unit_of_work as uow:
            task: TaskSchema | None = await uow.evaluations.get_task(
                task_id=task_id,
                team_id=team_id
            )
            if task is None:
                raise TaskNotFoundError()
            if task.status != TaskStatus.done:
                raise TaskNotDoneError()
            await uow.evaluations.create_evaluation(
                task_id=task_id,
                grader_id=actor_id,
                author_id=task.assignee_id,
                comment=data.comment_text,
                grade=data.grade
            )

    async def average_evaluations(self,
                                  user_id: IdType) -> GetAvgEvaluation:
        async with self.unit_of_work as uow:
            avg_eval = await uow.evaluations.average_evaluations(
                user_id=user_id,
            )
            if avg_eval is None:
                raise EvaluationsNotFoundError()
            return GetAvgEvaluation(average_evaluation=round(avg_eval, 2))
