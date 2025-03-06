from fastapi import APIRouter
from .profile import router as profile_router
from .collection import router as collection_router
from .collection_detail import router as collection_detail_router

public_router = APIRouter(prefix="", tags=["public"])
public_router.include_router(profile_router)
public_router.include_router(collection_router)
public_router.include_router(collection_detail_router)