import datetime as dt
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.dependencies.auth import id_from_access_token
from app.dependencies.calendar import calendar_service
from app.schemas.calendar import GetCalendarResponse
from app.schemas.types import IdType
from app.services.calendar import CalendarService

router = APIRouter(tags=['calendar'])


@router.get('/calendar',
            response_model=GetCalendarResponse,
            status_code=status.HTTP_200_OK)
async def get_calendar(
    actor_id: Annotated[IdType, Depends(id_from_access_token)],
    start: Annotated[dt.datetime, Query()],
    end: Annotated[dt.datetime, Query()],
    service: Annotated[CalendarService, Depends(calendar_service)]
) -> GetCalendarResponse:
    return await service.get_user_calendar(actor_id=actor_id,
                                           start=start,
                                           end=end)
