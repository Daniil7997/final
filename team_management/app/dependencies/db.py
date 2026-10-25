from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.infrastructure.db.connection import async_session_factory
from app.core.infrastructure.unit_of_work import UnitOfWork


async def get_sedssion() -> AsyncGenerator[AsyncSession]:
    async with async_session_factory() as session:
        yield session


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_unit_of_work(
        session: Annotated[AsyncSession, Depends(get_session)]
        ) -> UnitOfWork:
    return UnitOfWork(session)
