from app.core.config import settings
from app.core.infrastructure.redis.invite_storage import RedisInviteStorage
from app.core.infrastructure.storage.protocols import Storage


class InviteStore:

    def __init__(self, storage: Storage):
        self.storage = storage

    async def startup(self) -> None:
        await self.storage.connect()

    async def shutdown(self) -> None:
        await self.storage.close()

    async def get(self, key: str) -> str | None:
        return await self.storage.get(key)

    async def set(self, key: str,
                  value: str,
                  expire: int = settings.app.invite_code_ttl):
        await self.storage.set(
            key=key,
            value=value,
            expire=expire
        )


invite_storage = InviteStore(storage=RedisInviteStorage())
