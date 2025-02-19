from fastapi import FastAPI
from routes import users_router, profile_router, public_router
from connection import lifespan
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(lifespan=lifespan)

app.include_router(users_router)
app.include_router(profile_router)
app.include_router(public_router)