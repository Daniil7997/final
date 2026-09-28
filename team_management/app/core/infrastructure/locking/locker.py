from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class AdvisoryLocker:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def lock(self, key: int) -> None:
        await self.session.execute(
            text("SELECT pg_advisory_xact_lock(:key)"),
            {"key": key},
        )
