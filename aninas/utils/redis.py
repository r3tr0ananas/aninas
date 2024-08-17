from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    ...

import redis.asyncio as redis
import json

from ..constant import REDIS

class Redis:
    def __init__(self):
        pool = redis.ConnectionPool.from_url(REDIS)
        self.client = redis.Redis.from_pool(pool)
    
    async def get(self, id: str, return_json: bool = True) -> Optional[any]:
        data = await self.client.get(id)

        if data is not None:
            data = data.decode()

            if return_json:
                return json.loads(data)

            return data

        return None

    async def set(self, id: str, data: str, ex: int = 600, dump_json: bool = True) -> bool:
        if dump_json:
            data = json.dumps(data)

        return await self.client.set(id, data, ex)

    async def close(self):
        await self.client.aclose()