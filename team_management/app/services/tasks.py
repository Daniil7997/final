from app.domain.tasks.exceptions import TaskNotFoundError
from app.schemas.tasks import (
    ChangeTaskStatusRequest,
    ChangeTaskStatusResponse,
    CreateTaskCommentRequest,
    CreateTaskRequest,
    GetTaskResponse,
    UpdateTaskRequest,
    UpdateTaskResponse,
)
from app.schemas.types import IdType
from app.services.base import BaseService


class TasksService(BaseService):

    async def create_task(self,
                          data: CreateTaskRequest,
                          team_id: IdType,
                          creator_id: IdType):
        async with self.unit_of_work as uow:
            repo = uow.tasks
            await repo.create_task(
                description=data.description,
                due_date=data.due_date,
                creator_id=creator_id,
                team_id=team_id
                )
            return

    async def update_task(self,
                          data: UpdateTaskRequest,
                          team_id: IdType,
                          task_id: IdType) -> UpdateTaskResponse:
        async with self.unit_of_work as uow:

            task = await uow.tasks.update_task_by_id(
                update_data={
                    'description': data.description,
                    'due_date': data.due_date,
                    },
                team_id=team_id,
                task_id=task_id
                )
            if task is None:
                raise TaskNotFoundError()
            return UpdateTaskResponse.model_validate(task.model_dump())

    async def update_task_status(self,
                                 data: ChangeTaskStatusRequest,
                                 team_id: IdType,
                                 task_id: IdType) -> ChangeTaskStatusResponse:
        async with self.unit_of_work as uow:
            task = await uow.tasks.update_task_by_id(
                update_data={'status': data.new_status},
                team_id=team_id,
                task_id=task_id
                )
            if task is None:
                raise TaskNotFoundError()
            return ChangeTaskStatusResponse.model_validate(task.model_dump())

    async def delete_task_by_id(self,
                                team_id: IdType,
                                task_id: IdType) -> IdType:
        async with self.unit_of_work as uow:
            deleted_id = await uow.tasks.delete_task_by_id(
                task_id=task_id,
                team_id=team_id
                )
            if deleted_id is None:
                raise TaskNotFoundError()
            return deleted_id

    async def get_task_by_task_id(self,
                                  task_id: IdType,
                                  team_id: IdType):
        async with self.unit_of_work as uow:
            task = await uow.tasks.get_task_by_task_id(
                task_id=task_id,
                team_id=team_id
                )
            if task is None:
                raise TaskNotFoundError()
            return GetTaskResponse.model_validate(task.model_dump())

    async def create_task_comment(self,
                                  task_id: IdType,
                                  actor_id: IdType,
                                  data: CreateTaskCommentRequest) -> None:
        async with self.unit_of_work as uow:
            await uow.tasks.create_commment(
                task_id=task_id,
                actor_id=actor_id,
                comment_text=data.comment_text
                )
