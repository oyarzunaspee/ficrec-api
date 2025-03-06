from functools import wraps
from app.schemas import User, Token

def public_user(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        view = args[0]
        view.public = True
        view.base = "public"

        username = kwargs["username"]
        try:
            user = await User.find_by_username(username)
            if not user.is_active:
                raise view.not_found()
        except:
            raise view.server_problem()


        await view.redis.open()
        redis_key = f"public_user_{username}"
        redis_query = await view.redis.get_redis(redis_key)
        if redis_query:
            view.user_id = redis_query
        
        if not redis_query:
            view.user_id = str(user.id)
            await view.redis.set_redis(redis_key, str(user.id))

        return await func(*args, **kwargs)
    return wrapper

def auth_user(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        view = args[0]
        view.public = False
        view.base = "auth"

        token = kwargs["token"]
        view.user_id = Token(access_token=token).get_current_user()

        return await func(*args, **kwargs)
    return wrapper