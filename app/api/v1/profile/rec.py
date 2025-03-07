from fastapi import APIRouter, status, Cookie
from app.schemas import Rec
from app.utils.decorators import auth_user
from app.utils.handlers import QueryHandler
from app.utils.fastapi_class_view import View
from .collection_detail import UserCollectionItemView
from app.security.token import authorize_user

router = APIRouter()

# GET & POST COLLECTION RECS
@View(router, path="/collections/{reclist_id}/recs")
class UserRecsView(QueryHandler):
    RESPONSE_MODEL  = Rec
    parent_view     = UserCollectionItemView        # auth_collections_{reclist.id} 
    key             = "collections_detail_recs"     # auth_collections_{rec.id}

    @auth_user
    async def get(
            self, 
            reclist_id: str, 
            access_token: str | None = Cookie(default=None)
        ):

        redis_query = await self.redis_query(self.user_id)

        if redis_query:
            response = redis_query
        if not redis_query:
            response = await self.update_redis_item(reclist_id)

        await self.redis.close_redis()

        if not response:
            raise self.not_found()
        return response
    
    @auth_user
    async def post(
            self,
            reclist_id: str,
            rec_form: Rec,
            access_token: str | None = Cookie(default=None)
        ):
        created = await self.RESPONSE_MODEL.insert(rec_form)

        await self.redis.open()
        await self.update_redis_list(reclist_id)
        await self.redis.close_redis()

        return {"status": status.HTTP_201_CREATED, "created": created}

    @auth_user
    async def delete(
            self, 
            reclist_id: str,
            rec_id: str,
            access_token: str | None = Cookie(default=None)
        ):
        try:
            rec = await self.RESPONSE_MODEL.get(rec_id)
        except:
            raise self.not_found()

        if not authorize_user(access_token, rec.user_id):
            raise self.unauthorized()
        
        rec.deleted = True
        await rec.replace()

        await self.redis.open()
        await self.delete_redis_parent(reclist_id)
        await self.redis.close_redis()
            
        return {"status": status.HTTP_200_OK}