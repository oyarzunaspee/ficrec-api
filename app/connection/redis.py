from redis.asyncio import Redis
from app.security.config import settings
import pickle
from beanie import PydanticObjectId
from redis.retry import Retry
from redis.exceptions import (TimeoutError, ConnectionError)
from redis.backoff import ExponentialBackoff

class RedisClient:
    def __init__(self):
        super().__init__()

    async def open(self) -> None:
        self.client = await Redis(
            host=settings.REDIS_CACHE_HOST,
            port=settings.REDIS_CACHE_PORT,
            username=settings.REDIS_CACHE_USERNAME,
            password=settings.REDIS_CACHE_PASSWORD,
            decode_responses=False,
            retry=Retry(ExponentialBackoff(cap=10, base=1), 25), 
            retry_on_error = [
                ConnectionError, 
                TimeoutError, 
                ConnectionResetError
            ], 
            health_check_interval=1
        )

    async def get_redis(self, key: str) -> str:
        value = await self.client.get(key)
        if value:
            return pickle.loads(value)
    
    async def set_redis(self, key: str, value) -> None:
        pickled_value = pickle.dumps(value)
        await self.client.set(key, pickled_value)
    
    async def delete(self, key: str) -> None:
        await self.client.set(key, "")
        # neither delete or expire works
        await self.client.delete(key)

    async def scan(self, match: str):
        matched_keys = await self.client.scan(match)
        return matched_keys
    
    async def close_redis(self) -> None:
        await self.client.close()