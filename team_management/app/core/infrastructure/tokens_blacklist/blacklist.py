from app.core.config import settings
from app.core.infrastructure.redis.token_blacklist import RedisTokensBlacklist
from app.core.infrastructure.tokens_blacklist.protocols import (
    TokensBlacklistProtocol,
)


class TokensBlacklist:
    def __init__(self, blacklist: TokensBlacklistProtocol):
        self.blacklist = blacklist

    async def startup(self) -> None:
        await self.blacklist.connect()

    async def shutdown(self) -> None:
        await self.blacklist.close()

    async def get(self, key: str) -> str | None:
        return await self.blacklist.get(key)

    async def set(self, key: str,
                  value: str,
                  expire: int = settings.app.invite_code_ttl):
        await self.blacklist.set(
            key=key,
            value=value,
            expire=expire
        )


tokens_blacklist = TokensBlacklist(blacklist=RedisTokensBlacklist())
