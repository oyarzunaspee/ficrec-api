from fastapi import APIRouter
from .login import router as login_router
from .signup import router as signup_router

auth_router = APIRouter(prefix="/auth", tags=["auth"])
auth_router.include_router(login_router)
auth_router.include_router(signup_router)