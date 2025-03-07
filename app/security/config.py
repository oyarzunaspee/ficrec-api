import os
# from enum import Enum

from pydantic_settings import BaseSettings
from starlette.config import Config

current_file_dir = os.path.dirname(os.path.realpath(__file__))
env_path = os.path.join(current_file_dir, "..", ".env")
config = Config(env_path)


class AppSettings(BaseSettings):
    APP_NAME: str = config("APP_NAME", default="FastAPI app")
    APP_DESCRIPTION: str | None = config("APP_DESCRIPTION", default=None)

class CryptSettings(BaseSettings):
    SECRET_KEY: str = config("SECRET_KEY")
    ALGORITHM: str = config("ALGORITHM")
    ACCESS_TOKEN_EXPIRE: int = config("ACCESS_TOKEN_EXPIRE", default=1)


class MongoDBSettings(BaseSettings):
    MONGO_URI: str = config("MONGO_URI")


class RedisCacheSettings(BaseSettings):
    REDIS_CACHE_HOST: str = config("REDIS_CACHE_HOST", default="localhost")
    REDIS_CACHE_PORT: int = config("REDIS_CACHE_PORT")
    REDIS_CACHE_USERNAME: str = config("REDIS_CACHE_USERNAME")
    REDIS_CACHE_PASSWORD: str = config("REDIS_CACHE_PASSWORD")


# class RedisRateLimiterSettings(BaseSettings):
#     REDIS_RATE_LIMIT_HOST: str = config("REDIS_RATE_LIMIT_HOST", default="localhost")
#     REDIS_RATE_LIMIT_PORT: int = config("REDIS_RATE_LIMIT_PORT", default=6379)
#     REDIS_RATE_LIMIT_URL: str = f"redis://{REDIS_RATE_LIMIT_HOST}:{REDIS_RATE_LIMIT_PORT}"


class DefaultRateLimitSettings(BaseSettings):
    DEFAULT_RATE_LIMIT_LIMIT: int = config("DEFAULT_RATE_LIMIT_LIMIT", default=10)
    DEFAULT_RATE_LIMIT_PERIOD: int = config("DEFAULT_RATE_LIMIT_PERIOD", default=3600)


# class EnvironmentOption(Enum):
#     LOCAL = "local"
#     STAGING = "staging"
#     PRODUCTION = "production"


# class EnvironmentSettings(BaseSettings):
#     ENVIRONMENT: EnvironmentOption = config("ENVIRONMENT", default="local")


class Settings(
    AppSettings,
    CryptSettings,
    MongoDBSettings,
    RedisCacheSettings,
    # RedisRateLimiterSettings,
    DefaultRateLimitSettings,
    # EnvironmentSettings,
):
    pass


settings = Settings()