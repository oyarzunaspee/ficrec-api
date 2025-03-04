from fastapi import APIRouter, HTTPException, status, Depends, Form
from .models import User, Token, RecList, RecListConfig, Rec
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_class import endpoint
from .fastapi_class_view import View
from .handlers import QueryHandler
import nh3
from .decorators import public_user, auth_user
from .models import UserForm
from fastapi_problem.error import BadRequestProblem


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


auth_router = APIRouter(prefix="/auth", tags=["auth"])
profile_router = APIRouter(prefix="/profile", tags=["profile"])
public_router = APIRouter(prefix="", tags=["public"])



"""
FOR AUTH
"""

# POST NEW USER (REGISTER)
@auth_router.post("/signup")
async def create_user(
        user_form: UserForm
    ):
    user_exists = await User.find_by_username(user_form.username)
    if user_exists:
        raise BadRequestProblem(detail="Username already taken")

    if user_form.password != user_form.match_password:
        raise BadRequestProblem(detail="Passwords do not match")
    
    new_user = User(
        username = user_form.username,
        password = UserForm.hash_password(user_form.password)
    )
    await User.insert(new_user)
    return {"status": status.HTTP_201_CREATED}



# POST FOR TOKEN (LOG IN)
@auth_router.post("/login")
async def login(
        user_form: Annotated[OAuth2PasswordRequestForm, Depends()]
    ):
    
    user_exists = await User.find_by_username(nh3.clean(user_form.username))
    if user_exists is None:
        return HTTPException(status.HTTP_403_FORBIDDEN, detail="Wrong username or password")
    
    verify_password = user_exists.verify_password(nh3.clean(user_form.password))
    if verify_password is False:
        return HTTPException(status.HTTP_403_FORBIDDEN, detail="Wrong username or password")
    
    token = Token.create_access_token(user_exists)

    return {"status": status.HTTP_200_OK, "access_token": token}



"""
AUTHENTICATED
"""


# GET USER PROFILE
@View(profile_router)
class UserProfileView(QueryHandler):
    RESPONSE_MODEL  = User
    key             = "profile"   # user_profile_{user.id}

    @auth_user
    async def get(self, token: Token = Depends(oauth2_scheme)):
        redis_query = await self.redis_query(self.user_id)

        if redis_query:
            response = redis_query
        if not redis_query:
            response = await self.update_redis_item(self.user_id)
        await self.redis.close_redis()

        return response


# GET & POST USER COLLECTIONS
@View(profile_router, path="/collections")
class UserCollectionsView(QueryHandler):
    RESPONSE_MODEL  = RecList
    key             = "collections"   # user_collections_{user.id}

    @auth_user
    async def get(self, token: Token = Depends(oauth2_scheme)):
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

        new_reclist = self.RESPONSE_MODEL(name=nh3.clean(name), user_id=current_user_id, config=RecListConfig())
        created = await self.RESPONSE_MODEL.insert(new_reclist)

        await self.redis.open()
        await self.update_redis_list(self.user_id)
        await self.redis.close_redis()

        return {"status": status.HTTP_201_CREATED, "created": created}


# GET & PUT & DELETE COLLECTION
@View(profile_router, path="/collections/{reclist_id}")
class UserCollectionItemView(QueryHandler):
    RESPONSE_MODEL  = RecList
    parent_view     = UserCollectionsView   # user_collections_{user.id}
    key             = "collections_detail"    # user_collections_detail_{reclist.id}

    @auth_user
    async def get(self, reclist_id: str, token: Token = Depends(oauth2_scheme)):
        redis_query = await self.redis_query(reclist_id)
        
        if redis_query:
            response = redis_query
        if not redis_query:
            response = await self.update_redis_item(reclist_id)

        await self.redis.close_redis()
        return response

    @endpoint(("PUT"))
    @auth_user
    async def update(
            self, 
            reclist_id: str,
            reclist_form: RecList,
            token: Token = Depends(oauth2_scheme),
        ):
        reclist = await self.RESPONSE_MODEL.get(reclist_id)
  
        if not self.AUTH.authorize_user(token, reclist.user_id):
            raise self.unauthorized()
            
        if reclist_form.name is not None:
            reclist.name = nh3.clean(reclist_form.name)
        if reclist_form.about is not None:
            reclist.about = nh3.clean(reclist_form.about)
        await reclist.replace()


        await self.redis.open()
        # update individual item in redis
        await self.update_redis_item(reclist_id)
        # update list that contains item in redis
        await self.update_redis_parent(self.user_id)
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
        reclist = await self.RESPONSE_MODEL.get(reclist_id)


        if not self.AUTH.authorize_user(token, reclist.user_id):
            raise self.unauthorized()
            
        reclist.private = private
        await reclist.replace()

        await self.redis.open()
        # update individual item in redis
        await self.update_redis_item(reclist_id)
        # update list that contains item in redis
        await self.update_redis_parent(self.user_id)
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

        reclist = await self.RESPONSE_MODEL.get(reclist_id)

        if not self.AUTH.authorize_user(token, reclist.user_id):
            raise self.unauthorized()
            
        reclist.config = config_form
        await reclist.replace()

        await self.redis.open()
        # update individual item in redis
        await self.update_redis_item(reclist_id)
        # update list that contains item in redis
        await self.update_redis_parent(self.user_id)
        await self.redis.close_redis()
            
        return {"status": status.HTTP_200_OK}

    @endpoint(("DELETE"))
    @auth_user
    async def delete(
            self, 
            reclist_id: str,
            token: Token = Depends(oauth2_scheme),
        ):
        reclist = await self.RESPONSE_MODEL.get(reclist_id)
        if not self.AUTH.authorize_user(token, reclist.user_id):
            raise self.unoauthorized()
        
        reclist.deleted = True
        await reclist.replace()

        await self.redis.open()
        # update individual item in redis
        await self.update_redis_item(reclist_id)
        # update list that contains item in redis
        await self.update_redis_parent(self.user_id)
        await self.redis.close_redis()

            
        return {"status": status.HTTP_200_OK}


# GET & POST COLLECTION RECS
@View(profile_router, path="/collections/{reclist_id}/recs")
class UserRecsView(QueryHandler):
    RESPONSE_MODEL  = Rec
    parent_view     = UserCollectionItemView      # user_collections_{reclist.id} 
    key             = "collections_detail_recs"     # user_collections_{rec.id}

    @auth_user
    async def get(self, reclist_id: str, token: Token = Depends(oauth2_scheme)):

        redis_query = await self.redis_query(self.user_id)

        if redis_query:
            response = redis_query
        if not redis_query:
            response = await self.update_redis_item(reclist_id)

        await self.redis.close_redis()

        return response
    
    @auth_user
    async def post(
            self,
            reclist_id: str,
            rec_form: Rec,
            token: Token = Depends(oauth2_scheme)
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
            token: Token = Depends(oauth2_scheme),
        ):

        rec = await self.RESPONSE_MODEL.get(rec_id)

        if not self.AUTH.authorize_user(token, rec.user_id):
            raise self.unauthorized()
        
        rec.deleted = True
        await rec.replace()

        await self.redis.open()
        await self.update_redis_list(reclist_id)
        await self.redis.close_redis()
            
        return {"status": status.HTTP_200_OK}



"""
PUBLIC
"""

# GET USER PROFILE
@View(public_router, path="/{username}")
class ProfileView(QueryHandler):
    RESPONSE_MODEL  = User
    key             = "profile"   # public_profile_{user.id}

    @public_user
    async def get(self, username: str):
        redis_query = await self.redis_query(self.user_id)

        if redis_query:
            response = redis_query
        if not redis_query:
            response = await self.update_redis_item(self.user_id)
            await self.redis.close_redis()
        return response


# GET USER COLLECTIONS
@View(public_router, path="/{username}/collections")
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


# GET USER COLLECTION RECS
@View(public_router, path="/{username}/collections/{reclist_id}")
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