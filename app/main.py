from fastapi import FastAPI
from app.db.mongodb import lifespan
from dotenv import load_dotenv
import fastapi_problem.handler
from .api import router

load_dotenv()
app = FastAPI(lifespan=lifespan)
fastapi_problem.handler.add_exception_handler(app)


app.include_router(router)