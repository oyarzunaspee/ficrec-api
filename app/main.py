from fastapi import FastAPI
from .routes import auth_router, profile_router, public_router
from .connection import lifespan
from dotenv import load_dotenv
import fastapi_problem.handler
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()
app = FastAPI(lifespan=lifespan)
fastapi_problem.handler.add_exception_handler(app)


app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(public_router)