from models import Token
from connection import RedisClient
from fastapi_problem.error import ServerProblem, BadRequestProblem, UnauthorisedProblem

class QueryHandler:
    AUTH = Token
    redis = RedisClient()
    server_problem = ServerProblem
    bad_request = BadRequestProblem
    unauthorized = UnauthorisedProblem

    def __init__(self):
        self.redis = RedisClient()
        super().__init__()
    
    def redis_key(self, query_id: str):
        return f"{self.base}_{self.key}_{query_id}"
    
    async def redis_query(self, query_id: str):
        redis_key = self.redis_key(query_id)
        await self.redis.open()
        return await self.redis.get_redis(redis_key)

    async def update_redis_item(self, query_id: str):
        redis_key = self.redis_key(query_id)
        value = await self.RESPONSE_MODEL.query_item(
                    query_id,
                    self.public
                )
        await self.redis.set_redis(redis_key, value)
        return value

    async def update_redis_list(self, query_id):
        redis_key = self.redis_key(query_id)
        value = await self.RESPONSE_MODEL.query(
                query_id,
                self.public
            )
        await self.redis.set_redis(redis_key, value)
        return value
    
    async def update_redis_parent(self, query_id):
        redis_key = f"{self.base}_{self.parent_view.key}_{query_id}"
        value = await self.RESPONSE_MODEL.query(
            query_id,
            self.public
        )
        await self.redis.set_redis(redis_key, value)
        return value