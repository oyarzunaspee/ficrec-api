from fastapi import APIRouter, status, Depends, Form
from app.schemas import Token, RecList, RecListConfig, ReclistForm
from typing import Annotated
from fastapi_class import endpoint
from app.utils.decorators import auth_user
from app.security.oauth import oauth2_scheme
from app.utils.handlers import QueryHandler
from app.utils.fastapi_class_view import View
from .collection import UserCollectionsView

router = APIRouter()

# GET & PUT & DELETE COLLECTION
@View(router, path="/collections/{reclist_id}")
class UserCollectionItemView(QueryHandler):
    RESPONSE_MODEL  = RecList
    parent_view     = UserCollectionsView       # auth_collections_{user.id}
    key             = "collections_detail"      # auth_collections_detail_{reclist.id}

    @auth_user
    async def get(
            self, 
            reclist_id: str, 
            token: Token = Depends(oauth2_scheme)
        ):
        redis_query = await self.redis_query(reclist_id)
        
        if redis_query:
            response = redis_query
        if not redis_query:
            response = await self.update_redis_item(reclist_id)

        await self.redis.close_redis()
        if not response:
            raise self.not_found()
        return response

    @endpoint(("PUT"))
    @auth_user
    async def update(
            self, 
            reclist_id: str,
            reclist_form: ReclistForm,
            token: Token = Depends(oauth2_scheme),
        ):
        try:
            reclist = await self.RESPONSE_MODEL.get(reclist_id)
        except:
            raise self.not_found()
  
        if not self.AUTH.authorize_user(token, reclist.user_id):
            raise self.unauthorized()
            
        if reclist_form.name is not None:
            reclist.name = reclist_form.name
        if reclist_form.about is not None:
            reclist.about = reclist_form.about
        await reclist.replace()


        await self.redis.open()
        await self.delete_redis_item(reclist_id)
        await self.delete_redis_parent(self.user_id)
        await self.redis.close_redis()

        return {"status": status.HTTP_200_OK}

    @endpoint(("PUT"), path="/privacy")
    @auth_user
    async def update_privacy(
            self, 
            reclist_id: str,
            private: Annotated[bool, Form(...)],
            token: Token = Depends(oauth2_scheme),
        ):
        try:
            reclist = await self.RESPONSE_MODEL.get(reclist_id)
        except:
            raise self.not_found()


        if not self.AUTH.authorize_user(token, reclist.user_id):
            raise self.unauthorized()
            
        reclist.private = private
        await reclist.replace()

        await self.redis.open()
        await self.delete_redis_item(reclist_id)
        await self.delete_redis_parent(self.user_id)
        await self.redis.close_redis()
 
            
        return {"status": status.HTTP_200_OK}

    @endpoint(("PUT"), path="/config")
    @auth_user
    async def update_config(
            self, 
            reclist_id: str,
            config_form: RecListConfig,
            token: Token = Depends(oauth2_scheme),
        ):
        try:
            reclist = await self.RESPONSE_MODEL.get(reclist_id)
        except:
            raise self.not_found()

        if not self.AUTH.authorize_user(token, reclist.user_id):
            raise self.unauthorized()
            
        reclist.config = config_form
        await reclist.replace()

        await self.redis.open()
        await self.delete_redis_item(reclist_id)
        await self.delete_redis_parent(self.user_id)
        await self.redis.close_redis()
            
        return {"status": status.HTTP_200_OK}

    @endpoint(("DELETE"))
    @auth_user
    async def delete(
            self, 
            reclist_id: str,
            token: Token = Depends(oauth2_scheme),
        ):
        try:
            reclist = await self.RESPONSE_MODEL.get(reclist_id)
        except:
            raise self.not_found()
        if not self.AUTH.authorize_user(token, reclist.user_id):
            raise self.unoauthorized()
        
        reclist.deleted = True
        await reclist.replace()

        await self.redis.open()
        await self.delete_redis_item(reclist_id)
        await self.delete_redis_parent(self.user_id)
        await self.redis.close_redis()

        return {"status": status.HTTP_200_OK}