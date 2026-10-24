from sqlalchemy.ext.asyncio import AsyncSession

from app.core.infrastructure.db.repositories import (UsersRepo,
                              TeamsRepo,
                              TasksRepo,
                              EvaluationsRepo,
                              MeetingsRepo)
from app.core.infrastructure.locking.locker import AdvisoryLocker
from app.core.infrastructure.locking.key_factory import KeyFactory


class UnitOfWork():
    def __init__(self, session: AsyncSession):
        self.session = session

    async def __aenter__(self):
        self.locker = AdvisoryLocker(self.session)
        self.key_factory = KeyFactory()
        self.users = UsersRepo(self.session)
        self.teams = TeamsRepo(self.session)
        self.tasks = TasksRepo(self.session)
        self.evaluations = EvaluationsRepo(self.session)
        self.meetings = MeetingsRepo(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def lock(self, key: int):
        await self.locker.lock(key)
