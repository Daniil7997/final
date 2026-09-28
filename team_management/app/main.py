from typing import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.routers import main_v1_router
from app.api.handlers.register_handlers import register_all_handlers
from app.core.infrastructure.storage.invite import invite_storage
import app.models   # noqa F401


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    import app.logger_config  # noqa

    await invite_storage.startup()
    yield
    await invite_storage.shutdown()


application = FastAPI(lifespan=lifespan)

application.include_router(main_v1_router)


register_all_handlers(app=application)
