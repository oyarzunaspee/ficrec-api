from fastapi import APIRouter, status, Cookie
from app.schemas import User, UserProfileForm, UsernameForm, PasswordForm
from app.utils.fastapi_class_view import View
from app.utils.handlers import QueryHandler
from app.utils.decorators import auth_user
from fastapi_class import endpoint

router = APIRouter()

@View(router)
class UserProfileView(QueryHandler):
    RESPONSE_MODEL  = User
    key             = "profile"   # auth_profile_{user.id}

    @auth_user
    async def get(
            self, 
            access_token: str | None = Cookie(default=None)
        ):
        redis_query = await self.redis_query(self.user_id)

        if redis_query:
            response = redis_query
        if not redis_query:
            response = await self.update_redis_item(self.user_id)
        await self.redis.close_redis()

        return response
    
    @endpoint(("PUT"))
    @auth_user
    async def update(
            self, 
            user_form: UserProfileForm,
            access_token: str | None = Cookie(default=None)
        ):
        try:
            user = User.get(self.user_id)
        except:
            raise self.server_problem()
        
        if user_form.bio:
            user.bio = user_form.bio
        if user_form.avatar:
            user_form.avatar = user_form.avatar
        await user.replace()

        await self.redis.open()
        await self.delete_redis_item(self.user_id)
        await self.redis.close_redis()
    
    @endpoint(("PUT"), path="/username")
    @auth_user
    async def update(
            self, 
            username_form: UsernameForm,
            access_token: str | None = Cookie(default=None)
        ):
        user = User.get(self.user_id)

        user_exists = await User.find_by_username(username_form.username)
        if user_exists:
            raise self.bad_request(detail="Username already taken")
   
        user.username = username_form.username
        await user.replace()

        await self.redis.open()
        await self.delete_redis_item(self.user_id)
        await self.redis.close_redis()

    
    @endpoint(("PUT"), path="/password")
    @auth_user
    async def update(
            self, 
            password_form: PasswordForm,
            access_token: str | None = Cookie(default=None)
        ):
        try:
            user = User.get(self.user_id)
        except:
            raise self.server_problem()
        
        if password_form.password != password_form.match_password:
            raise self.bad_request()

        user.password = PasswordForm.hash_password(password_form.password)
        await user.replace()

    @endpoint(("PUT"), path="deactivate")
    @auth_user
    async def update(
            self, 
            access_token: str | None = Cookie(default=None)
        ):
        try:
            user = User.get(self.user_id)
        except:
            raise self.server_problem()

        try:
            self.redis_deactivate()
        except:
            raise self.server_problem()
        
        await self.redis.close_redis()

        user.is_active = True
        await user.replace()

        return {"status": status.HTTP_200_OK}