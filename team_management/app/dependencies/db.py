from typing import Annotated, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.core.infrastructure.unit_of_work import UnitOfWork
from app.core.infrastructure.db.connection import async_session_factory


async def get_sedssion() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session


async def get_session() -> AsyncGenerator[AsyncSession, None]:
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
