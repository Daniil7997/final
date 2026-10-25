from app.core.infrastructure.redis.token_blacklist import RedisTokensBlacklist
from app.core.infrastructure.tokens_blacklist.protocols import (
    TokensBlacklistProtocol,
)


class TokensBlacklist:
    def __init__(self, storage: TokensBlacklistProtocol):
        self.storage = storage

    async def startup(self) -> None:
        await self.storage.connect()

    async def shutdown(self) -> None:
        await self.storage.close()

    async def get(self, key: str) -> str | None:
        return await self.storage.get(key)

    async def set(self,
                  key: str,
                  value: str,
                  expire: int):
        await self.storage.set(
            key=key,
            value=value,
            expire=expire
        )


tokens_blacklist = TokensBlacklist(storage=RedisTokensBlacklist())
