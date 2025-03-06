from fastapi import APIRouter
from app.schemas import RecList
from app.utils.fastapi_class_view import View
from app.utils.handlers import QueryHandler
from app.utils.decorators import public_user

router = APIRouter()

@View(router, path="/{username}/collections")
class PublicProfileView(QueryHandler):
    RESPONSE_MODEL  = RecList
    key             = "collections"   # public_collections_{user.id}

    @public_user
    async def get(self, username: str):
        redis_query = await self.redis_query(self.user_id)

        
        if redis_query:
            response = redis_query
        if not redis_query:
            response = await self.update_redis_list(self.user_id)

        await self.redis.close_redis()

        return response