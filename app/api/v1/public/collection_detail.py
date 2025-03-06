from fastapi import APIRouter
from app.schemas import Rec
from app.utils.fastapi_class_view import View
from app.utils.handlers import QueryHandler
from app.utils.decorators import public_user

router = APIRouter()

# GET USER COLLECTION RECS
@View(router, path="/{username}/collections/{reclist_id}")
class PublicRecsView(QueryHandler):
    RESPONSE_MODEL  = Rec
    key             = "collection_detail_recs"   # public_collections_recs_{reclist.id}

    @public_user
    async def get(self, username: str, reclist_id: str):
        redis_query = await self.redis_query(reclist_id)
        
        if redis_query:
            response = redis_query
        if not redis_query:
            response = await self.update_redis_list(reclist_id)

        await self.redis.close_redis()
        return response