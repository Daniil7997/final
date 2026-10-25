import logging

from pydantic_settings import BaseSettings, SettingsConfigDict

log = logging.getLogger('CONFIG')


class SharedConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file='envs/.env.local',
                                      env_file_encoding='utf-8',
                                      extra='ignore')


class DatabaseSettings(SharedConfig):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    IS_TEST_DB: bool = False

    @property
    def url_async_sqlalchemy(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )

    @property
    def url_asyncpg(self) -> str:
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )

    @property
    def ready_for_test(self) -> bool:
        return bool(self.IS_TEST_DB is True and 'test' in self.DB_NAME.lower())


class RedisSettings(SharedConfig):
    REDIS_PASSWORD: str
    REDIS_PORT: int
    REDIS_HOST: str

    @property
    def _base_url(self):
        return (f'redis://:{self.REDIS_PASSWORD}'
                f'@{self.REDIS_HOST}:{self.REDIS_PORT}')

    @property
    def url_invite_storage(self) -> str:
        return self._base_url + '/0'

    @property
    def url_token_blacklist(self) -> str:
        return self._base_url + '/1'


class ApplicationSettings(SharedConfig):
    PRIVATE_KEY_HEX: str
    hashed_admin_password: str

    @property
    def access_tokens_ttl(self) -> int:
        return 72 * 60 * 60

    @property
    def invite_code_ttl(self) -> int:
        return 72 * 60 * 60


class AggregateSettings:
    def __init__(self) -> None:
        self.db = DatabaseSettings()  # type: ignore[call-arg]
        self.redis = RedisSettings()  # type: ignore[call-arg]
        self.app = ApplicationSettings()  # type: ignore[call-arg]


settings = AggregateSettings()
