from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI
from contextlib import asynccontextmanager
import certifi
from beanie import init_beanie
from app.schemas import User, RecList, Rec

from app.security.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    await startup_db_client(app)
    yield
    await shutdown_db_client(app)

async def startup_db_client(app: FastAPI) -> None:
    app.mongodb_client = AsyncIOMotorClient(
        settings.MONGO_URI,
        tlsCAFile=certifi.where()
    )
    await init_beanie(database=app.mongodb_client.ficrec, document_models=[User, RecList, Rec])

async def shutdown_db_client(app: FastAPI) -> None:
    app.mongodb_client.close()