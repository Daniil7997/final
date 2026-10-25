import uuid
from collections.abc import AsyncGenerator
from datetime import UTC, date, datetime, timedelta

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    AsyncTransaction,
    create_async_engine,
)
from sqlalchemy.ext.asyncio import async_sessionmaker as as_sessionmaker

from app.core.config import settings
from app.core.infrastructure.db.models.meetings import Meetings
from app.core.infrastructure.db.models.tasks import Tasks
from app.core.infrastructure.db.models.teams import Teams
from app.core.infrastructure.db.models.users import Users
from app.core.infrastructure.storage.invite import invite_storage
from app.core.security import create_tokens, hash_password
from app.core.utils import generate_invite_code
from app.dependencies.db import get_session
from app.main import application
from tests.factories import AggregateFactory


@pytest.fixture(scope='session')
async def async_engine() -> AsyncEngine:
    engine: AsyncEngine = create_async_engine(
        url=settings.db.url_async_sqlalchemy,
        echo=False,
    )
    return engine


@pytest.fixture(scope='function')
async def test_session(async_engine) -> AsyncGenerator[AsyncSession]:
    async with async_engine.connect() as conn:
        trans: AsyncTransaction = await conn.begin()
        async_session = as_sessionmaker(
            bind=conn,
            expire_on_commit=False,
        )
        session = async_session()
        try:
            yield session
        finally:
            await session.close()
            await trans.rollback()


@pytest.fixture(scope="function", autouse=True)
async def db_overrides(test_session):

    def override_get_session():
        return test_session

    application.dependency_overrides[get_session] = override_get_session
    yield
    application.dependency_overrides.clear()


@pytest.fixture
def api_prefix():
    return "/api/v1"


@pytest.fixture
async def async_client():
    async with LifespanManager(app=application):
        transport = ASGITransport(app=application)
        async with AsyncClient(transport=transport,
                               base_url='http://test') as client:
            yield client


@pytest.fixture(scope='function')
async def aggregate_factory(test_session) -> AggregateFactory:
    return AggregateFactory(test_session)


@pytest.fixture(scope='function')
async def user_admin(aggregate_factory: AggregateFactory):
    password = "admin123"
    hashed_password = hash_password(password)
    user = await aggregate_factory.users.create_user(
        email=f"{uuid.uuid4()}@gmail.com",
        name="IvanAdmin",
        hashed_password=hashed_password,
        is_admin=True
        )
    user.password = password
    return user


@pytest.fixture(scope='function')
async def user_no_team(aggregate_factory: AggregateFactory):
    password = "secret123"
    hashed_password = hash_password(password)
    user = await aggregate_factory.users.create_user(
        email=f"{uuid.uuid4()}@gmail.com",
        name="IvanNoTeam",
        hashed_password=hashed_password
        )
    user.password = password
    return user


@pytest.fixture(scope='function')
async def user_member(aggregate_factory: AggregateFactory,
                      team: Teams):
    password = "secret1password"
    hashed_password = hash_password(password)
    user = await aggregate_factory.users.create_user(
        email=f"{uuid.uuid4()}@gmail.com",
        name="IvanTeamMember",
        hashed_password=hashed_password
        )
    await aggregate_factory.teams.join_team(team_id=team.id, user_id=user.id)
    user.password = password
    return user


@pytest.fixture(scope='function')
async def user_manager(_user_manager: Users,
                       team: Teams):
    return _user_manager


@pytest.fixture(scope='function')
async def _user_manager(aggregate_factory: AggregateFactory):

    password = "secret1password"
    hashed_password = hash_password(password)
    user = await aggregate_factory.users.create_user(
        email=f"{uuid.uuid4()}@gmail.com",
        name="IvanTeamManager",
        hashed_password=hashed_password
        )
    user.password = password
    return user


@pytest.fixture(scope='function')
def member_tokens(user_member: Users):
    return create_tokens(user_id=user_member.id)


@pytest.fixture(scope='function')
def manager_tokens(user_manager: Users):
    return create_tokens(user_id=user_manager.id)


@pytest.fixture(scope='function')
def admin_tokens(user_admin: Users):
    return create_tokens(user_id=user_admin.id)


@pytest.fixture(scope='function')
def user_no_team_tokens(user_no_team: Users):
    return create_tokens(user_id=user_no_team.id)


@pytest.fixture(scope='function')
async def team(
    aggregate_factory: AggregateFactory,
    _user_manager: Users
) -> Teams:
    team = await aggregate_factory.teams.create_team(
        name='SuperTeam',
        manager_id=_user_manager.id,
        description='My large team for developing cool apps',
    )
    return team


@pytest.fixture(scope='function')
async def team_invite_code(team: Teams) -> str:
    invite_code = generate_invite_code()
    await invite_storage.set(key=invite_code, value=str(team.id))
    return invite_code


@pytest.fixture(scope='function')
async def task(team: Teams,
               user_manager: Users,
               aggregate_factory: AggregateFactory) -> Tasks:
    due_date = date.today() + timedelta(days=3)
    return await aggregate_factory.tasks.create_task(
        description="test_task",
        due_date=due_date,
        creator_id=user_manager.id,
        team_id=team.id
    )


@pytest.fixture(scope='function')
async def meeting(team: Teams,
                  aggregate_factory: AggregateFactory) -> Meetings:
    start_meeting = datetime.now(UTC) + timedelta(hours=1)
    end_meeting = start_meeting + timedelta(hours=1)
    return await aggregate_factory.meetings.create_meeting(
        description="some text",
        start_meeting=start_meeting,
        end_meeting=end_meeting,
        team_id=team.id
    )
