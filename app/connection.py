from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI
from contextlib import asynccontextmanager
import certifi
from beanie import init_beanie
from .models import User, RecList, Rec
from redis.asyncio import Redis
import os
import pickle
from redis.retry import Retry
from redis.exceptions import (TimeoutError, ConnectionError)
from redis.backoff import ExponentialBackoff

@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_db_client(app)
    yield
    await shutdown_db_client(app)

async def startup_db_client(app):
    app.mongodb_client = AsyncIOMotorClient(
        os.getenv("URI"),
        tlsCAFile=certifi.where()
    )
    await init_beanie(database=app.mongodb_client.ficrec, document_models=[User, RecList, Rec])

async def shutdown_db_client(app):
    app.mongodb_client.close()


class RedisClient:
    def __init__(self):
        super().__init__()

    async def open(self):
        self.client = await Redis(
            host=os.getenv("REDIS_HOST"),
            port=os.getenv("REDIS_PORT"),
            username=os.getenv("REDIS_USERNAME"),
            password=os.getenv("REDIS_PW"),
            decode_responses=False,
            retry=Retry(ExponentialBackoff(cap=10, base=1), 25), 
            retry_on_error = [
                ConnectionError, 
                TimeoutError, 
                ConnectionResetError
            ], 
            health_check_interval=1
        )

    async def get_redis(self, key: str):
        value = await self.client.get(key)
        if value:
            return pickle.loads(value)
    
    async def set_redis(self, key: str, value):
        pickled_value = pickle.dumps(value)
        await self.client.set(key, pickled_value)
    
    async def close_redis(self):
        await self.client.close()