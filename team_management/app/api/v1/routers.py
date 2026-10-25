from fastapi import APIRouter

from app.api.v1.endpoints.admin import router as admin_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.calendar import router as calendar_router
from app.api.v1.endpoints.evaluations import router as evaluations_router
from app.api.v1.endpoints.meetings import router as meetings_router
from app.api.v1.endpoints.tasks import router as tasks_router
from app.api.v1.endpoints.teams import router as teams_router
from app.api.v1.endpoints.users import router as users_router

routers = [auth_router,
           users_router,
           teams_router,
           tasks_router,
           evaluations_router,
           meetings_router,
           calendar_router,
           admin_router]


main_v1_router = APIRouter(prefix='/api/v1')


for router in routers:
    main_v1_router.include_router(router)
