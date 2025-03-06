from fastapi import APIRouter
from .user import router as user_router
from .collection import router as collection_router
from .collection_detail import router as collection_detail_router
from .rec import router as rec_router

profile_router = APIRouter(prefix="/profile", tags=["profile"])
profile_router.include_router(user_router)
profile_router.include_router(collection_router)
profile_router.include_router(collection_detail_router)
profile_router.include_router(rec_router)