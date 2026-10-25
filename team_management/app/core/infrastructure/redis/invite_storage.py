import logging

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import settings
from app.core.infrastructure.exceptions import (
    InviteStorageNotConnectedError,
    InviteStorageUnavailableError,
)

log = logging.getLogger('redis_invite_storage')


class RedisInviteStorage:
    def __init__(self) -> None:
        self.redis: Redis | None = None

    async def connect(self) -> None:
        if self.redis is not None:
            return
        try:
            redis = Redis.from_url(
                settings.redis.url_invite_storage,
                encoding="utf-8",
                decode_responses=True
            )
            await redis.ping()
            self.redis = redis
        except RedisError:
            raise InviteStorageUnavailableError()

    def _get_client(self):
        if self.redis is None:
            raise InviteStorageNotConnectedError()
        return self.redis

    async def close(self) -> None:
        if self.redis is None:
            return
        try:
            await self.redis.aclose()
        except RedisError:
            raise InviteStorageUnavailableError()
        finally:
            self.redis = None

    async def clear(self) -> None:
        redis = self._get_client()
        try:
            await redis.flushdb()
        except RedisError:
            raise InviteStorageUnavailableError()

    async def get(self, key: str) -> str | None:
        redis = self._get_client()
        try:
            result = await redis.getdel(key)
        except RedisError:
            raise InviteStorageUnavailableError()
        return result

    async def set(
        self,
        key: str,
        value: str,
        expire: int,
    ) -> None:
        redis = self._get_client()
        try:
            await redis.setex(name=key, time=expire, value=value)
        except RedisError:
            raise InviteStorageUnavailableError()
