from fastapi import APIRouter
from app.api.v1.profile import profile_router
from app.api.v1.auth import auth_router
from app.api.v1.public import public_router

router = APIRouter(prefix="/v1")

router.include_router(auth_router)
router.include_router(profile_router)
router.include_router(public_router)