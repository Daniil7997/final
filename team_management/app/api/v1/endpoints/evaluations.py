from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status

from app.dependencies.auth import (
    id_from_access_token,
    required_manager_or_higher,
)
from app.dependencies.evaluations import evaluations_service
from app.schemas.common import SuccessMessageResponse
from app.schemas.evaluations import CreateEvaluationsRequest, GetAvgEvaluation
from app.schemas.types import IdType, TeamsRoleType
from app.services.evaluations import EvaluationsService

router = APIRouter(tags=["evaluations"])


@router.post('/teams/{team_id}/tasks/{task_id}/evaluations',
             status_code=status.HTTP_201_CREATED)
async def rate_task(
    actor_role: Annotated[TeamsRoleType, Depends(required_manager_or_higher)],
    actor_id: Annotated[IdType, Depends(id_from_access_token)],
    task_id: Annotated[IdType, Path()],
    team_id: Annotated[IdType, Path()],
    data: Annotated[CreateEvaluationsRequest, Body()],
    service: Annotated[EvaluationsService, Depends(evaluations_service)]
) -> SuccessMessageResponse:
    await service.create_evaluation(actor_id=actor_id,
                                    task_id=task_id,
                                    team_id=team_id,
                                    data=data)
    msg = "The evaluation has been successfully submitted."
    return SuccessMessageResponse(msg=msg)


@router.get('/users/me/evaluations',
            response_model=GetAvgEvaluation,
            status_code=status.HTTP_200_OK)
async def get_avg_evaluation(
    actor_id: Annotated[IdType, Depends(id_from_access_token)],
    service: Annotated[EvaluationsService, Depends(evaluations_service)]
) -> GetAvgEvaluation:
    return await service.average_evaluations(user_id=actor_id)
