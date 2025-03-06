from app.schemas import Token, RecList
from app.db.redis import RedisClient
from typing import List
from fastapi_problem.error import (
    ServerProblem, 
    BadRequestProblem, 
    UnauthorisedProblem, 
    NotFoundProblem,
    ConflictProblem
)

class QueryHandler:
    AUTH = Token

    redis = RedisClient()

    server_problem = ServerProblem
    bad_request = BadRequestProblem
    unauthorized = UnauthorisedProblem
    not_found = NotFoundProblem
    conflict = ConflictProblem

    def __init__(self):
        self.redis = RedisClient()
        super().__init__()
    
    def redis_key(self, query_id: str) -> str:
        return f"{self.base}_{self.key}_{query_id}"

    def update_redis_keys(self, query_id: str, parent: bool = False) -> list:
        match parent:
            case True:
                auth = f"auth_{self.parent_view.key}_{query_id}"
                public = f"public_{self.parent_view.key}_{query_id}"
            case False:
                auth = f"auth_{self.key}_{query_id}"
                public = f"public_{self.key}_{query_id}"
        return [auth, public]
    
    async def redis_query(self, query_id: str):
        redis_key = self.redis_key(query_id)
        await self.redis.open()
        return await self.redis.get_redis(redis_key)

    async def delete_redis_item(self, query_id: str) -> None:
        redis_keys = self.update_redis_keys(query_id)
        for key in redis_keys:
            await self.redis.delete(key)

    async def delete_redis_parent(self, query_id: str) -> None:
        redis_keys = self.update_redis_keys(query_id, parent=True)
        for key in redis_keys:
            await self.redis.delete(key)

    async def update_redis_item(self, query_id: str):
        redis_key = self.redis_key(query_id)
        value = await self.RESPONSE_MODEL.query_item(
                    query_id,
                    self.public
                )
        if value:
            await self.redis.set_redis(redis_key, value)
        return value

    async def update_redis_list(self, query_id: str) -> list:
        redis_key = self.redis_key(query_id)
        value = await self.RESPONSE_MODEL.query(
                query_id,
                self.public
            )
        if value:
            await self.redis.set_redis(redis_key, value)
        return value
    
    async def redis_deactivate(self) -> None:
        redis_keys = self.redis.scan(self.user_id)
        await self.scan_delete(redis_keys)

        reclists = RecList.query(self.user_id)
        for reclist in reclists:
            redis_reclist_keys = self.redis.scan(str(reclist.id))
            await self.scan_delete(redis_reclist_keys)

    async def scan_delete(self, redis_keys: List) -> None:
        for key in redis_keys:
            await self.redis.delete(key)