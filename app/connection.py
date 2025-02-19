from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI
from contextlib import asynccontextmanager
import certifi
from beanie import init_beanie
from models import User, RecList, Rec
import os

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