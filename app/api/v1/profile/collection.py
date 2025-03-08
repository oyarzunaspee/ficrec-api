from fastapi import APIRouter, status, Depends, Form
from app.schemas import Token, RecList, RecListConfig
from typing import Annotated
from app.utils.decorators import auth_user
from app.security.oauth import oauth2_scheme
from app.utils.handlers import QueryHandler
from app.utils.fastapi_class_view import View

router = APIRouter()

# GET & POST USER COLLECTIONS
@View(router, path="/collections")
class UserCollectionsView(QueryHandler):
    RESPONSE_MODEL  = RecList
    key             = "collections"   # auth_collections_{user.id}

    @auth_user
    async def get(
            self, 
            token: Token = Depends(oauth2_scheme)
        ):
        redis_query = await self.redis_query(self.user_id)
        
        if redis_query:
            response = redis_query
        if not redis_query:
            response = await self.update_redis_list(self.user_id)
        await self.redis.close_redis()
        return response
    
    @auth_user
    async def post(
            self,
            name: Annotated[str, Form(...)],
            token: Token = Depends(oauth2_scheme)
        ):
        current_user_id = self.AUTH(access_token=token).get_current_user()

        new_reclist = self.RESPONSE_MODEL(
            name=name, 
            user_id=current_user_id, 
            config=RecListConfig()
        )
        created = await self.RESPONSE_MODEL.insert(new_reclist)

        await self.redis.open()
        await self.delete_redis_item(self.user_id)
        await self.redis.close_redis()

        return {"status": status.HTTP_201_CREATED, "created": created}