from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status

from app.dependencies.auth import (
    id_from_access_token,
    required_manager_or_higher,
    required_member_or_higher,
)
from app.dependencies.tasks import tasks_service
from app.schemas.common import SuccessMessageResponse
from app.schemas.tasks import (
    ChangeTaskStatusRequest,
    ChangeTaskStatusResponse,
    CreateTaskCommentRequest,
    CreateTaskRequest,
    GetTaskResponse,
    UpdateTaskRequest,
    UpdateTaskResponse,
)
from app.schemas.types import IdType, TeamsRoleType
from app.services.tasks import TasksService

router = APIRouter(tags=["tasks"])


@router.post('/teams/{team_id}/tasks',
             status_code=status.HTTP_201_CREATED,
             response_model=SuccessMessageResponse)
async def create_task(
    team_role: Annotated[TeamsRoleType, Depends(required_manager_or_higher)],
    team_id: Annotated[IdType, Path()],
    creator_id: Annotated[IdType, Depends(id_from_access_token)],
    data: Annotated[CreateTaskRequest, Body()],
    service: Annotated[TasksService, Depends(tasks_service)]
) -> SuccessMessageResponse:
    await service.create_task(data=data,
                              creator_id=creator_id,
                              team_id=team_id)
    msg = "The task has been successfully created."
    return SuccessMessageResponse(msg=msg)


@router.put('/teams/{team_id}/tasks/{task_id}',
            response_model=UpdateTaskResponse,
            status_code=status.HTTP_200_OK)
async def edit_task_by_id(
    team_role: Annotated[TeamsRoleType, Depends(required_manager_or_higher)],
    team_id: Annotated[IdType, Path()],
    task_id: Annotated[IdType, Path()],
    data: Annotated[UpdateTaskRequest, Body()],
    service: Annotated[TasksService, Depends(tasks_service)]
) -> UpdateTaskResponse:
    return await service.update_task(team_id=team_id,
                                     task_id=task_id,
                                     data=data)


@router.delete('/teams/{team_id}/tasks/{task_id}',
               response_model=SuccessMessageResponse,
               status_code=status.HTTP_200_OK)
async def delete_task_by_id(
    team_role: Annotated[TeamsRoleType, Depends(required_manager_or_higher)],
    team_id: Annotated[IdType, Path()],
    task_id: Annotated[IdType, Path()],
    service: Annotated[TasksService, Depends(tasks_service)]
) -> SuccessMessageResponse:
    deleted_task_id = await service.delete_task_by_id(team_id=team_id,
                                                      task_id=task_id)
    msg = f'Successfully deleted task ID{deleted_task_id}'
    return SuccessMessageResponse(msg=msg)


@router.get('/teams/{team_id}/tasks/{task_id}',
            response_model=GetTaskResponse,
            status_code=status.HTTP_200_OK)
async def get_task_by_id(
    team_role: Annotated[TeamsRoleType, Depends(required_member_or_higher)],
    team_id: Annotated[IdType, Path()],
    task_id: Annotated[IdType, Path()],
    service: Annotated[TasksService, Depends(tasks_service)]
) -> GetTaskResponse:
    return await service.get_task_by_task_id(team_id=team_id,
                                             task_id=task_id)


@router.patch('/teams/{team_id}/tasks/{task_id}',
              response_model=ChangeTaskStatusResponse,
              status_code=status.HTTP_200_OK)
async def change_task_status_by_id(
    team_role: Annotated[TeamsRoleType, Depends(required_member_or_higher)],
    team_id: Annotated[IdType, Path()],
    task_id: Annotated[IdType, Path()],
    data: Annotated[ChangeTaskStatusRequest, Body()],
    service: Annotated[TasksService, Depends(tasks_service)]
) -> ChangeTaskStatusResponse:
    return await service.update_task_status(
        team_id=team_id,
        task_id=task_id,
        data=data
        )


@router.post('/teams/{team_id}/tasks/{task_id}/comments',
             response_model=SuccessMessageResponse,
             status_code=status.HTTP_201_CREATED)
async def create_comment(
    team_role: Annotated[TeamsRoleType, Depends(required_manager_or_higher)],
    task_id: Annotated[IdType, Path()],
    actor_id: Annotated[IdType, Depends(id_from_access_token)],
    data: Annotated[CreateTaskCommentRequest, Body()],
    service: Annotated[TasksService, Depends(tasks_service)]
) -> SuccessMessageResponse:
    await service.create_task_comment(actor_id=actor_id,
                                      task_id=task_id,
                                      data=data)
    msg = "The comment has been successfully created."
    return SuccessMessageResponse(msg=msg)
