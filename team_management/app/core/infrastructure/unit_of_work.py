import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.infrastructure.db.repositories import (
    EvaluationsRepo,
    MeetingsRepo,
    TasksRepo,
    TeamsRepo,
    UsersRepo,
)
from app.core.infrastructure.locking.key_factory import KeyFactory
from app.core.infrastructure.locking.locker import AdvisoryLocker


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def __aenter__(self):
        self.__locker = AdvisoryLocker(self.session)
        self.__key_factory = KeyFactory()
        self.users = UsersRepo(self.session)
        self.teams = TeamsRepo(self.session)
        self.tasks = TasksRepo(self.session)
        self.evaluations = EvaluationsRepo(self.session)
        self.meetings = MeetingsRepo(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def advisory_lock_from_list_uuid(self, array: list[uuid.UUID]):
        keys = self.__key_factory.create_lock_keys_from_list_uuid(array)
        await self.__locker.lock_list(keys)

    async def advisory_lock_from_uuid(self, value: list[uuid.UUID]):
        key = self.__key_factory.create_lock_key_from_uuid(value)
        await self.__locker.lock(key)
