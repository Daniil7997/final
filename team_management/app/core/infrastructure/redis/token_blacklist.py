from typing import cast

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import settings
from app.core.infrastructure.exceptions import TokensBlacklistUnavailableError


class RedisTokensBlacklist:
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
            pass

    async def close(self) -> None:
        if self.redis is None:
            return
        try:
            await self.redis.aclose()
        except RedisError:
            raise TokensBlacklistUnavailableError()
        finally:
            self.redis = None

    async def clear(self) -> None:
        redis = self.redis
        if redis is None:
            raise TokensBlacklistUnavailableError()
        try:
            await redis.flushdb()
        except RedisError:
            raise TokensBlacklistUnavailableError()

    async def get(self, key: str) -> str | None:
        redis = self.redis
        if redis is None:
            return None
        try:
            val = cast(str | None, await redis.get(key))
            return val
        except RedisError:
            return None

    async def set(
        self,
        key: str,
        value: str,
        expire: int,
    ) -> None:
        redis = self.redis
        if redis is None:
            return
        try:
            await redis.set(name=key, ex=expire, value=value)
        except RedisError:
            raise TokensBlacklistUnavailableError()
