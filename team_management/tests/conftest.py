import pytest

from app.core.config import settings


@pytest.fixture(scope="session", autouse=True)
def critical_check() -> None:
    if not settings.db.ready_for_test:
        pytest.exit(f"Остановка всех тестов: БАЗА ДАННЫХ {settings.db.DB_NAME} "
                    f"НЕ ДЛЯ ТЕСТИРОВАНИЯ.")


# @pytest.fixture(scope="session")
# def event_loop(critical_check):
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     yield loop
#     loop.close()


# @pytest.fixture(scope="session", autouse=True)
# async def init_lifespan_for_all_tests(critical_check, event_loop):
#     await invite_storage.startup()
#     yield
#     await invite_storage.shutdown()
