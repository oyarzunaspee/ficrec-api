from fastapi import FastAPI
# from .api.v1.routes import auth_router, profile_router, public_router
from app.db.mongodb import lifespan
from dotenv import load_dotenv
import fastapi_problem.handler
from fastapi.middleware.cors import CORSMiddleware
from .api import router
from app.security.config import settings

load_dotenv()
app = FastAPI(lifespan=lifespan)
fastapi_problem.handler.add_exception_handler(app)


app.include_router(router)