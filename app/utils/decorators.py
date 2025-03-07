from functools import wraps
from app.schemas import User
from app.security.token import get_current_user

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

        token = kwargs["access_token"]
        if not token:
            raise view.unauthorized("Please log in")

        view.user_id = get_current_user(token.split(" ")[1])

        return await func(*args, **kwargs)
    return wrapper