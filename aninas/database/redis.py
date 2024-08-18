from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional

import redis.asyncio as redis
import json

from ..constant import REDIS

__all__ = ("Redis", )

class Redis:
    def __init__(self):
        self.client = redis.Redis.from_url(REDIS)
    
    async def get(
        self, 
        id: str,
        _json: bool = True
    ) -> Optional[bytes] | Optional[dict]:
        cache = await self.client.get(id)

        if cache:
            if _json:
                cache = json.loads(cache)

            return cache

        return None
    
    async def set(
        self,
        id: str,
        data: any,
        expire: int = 600,
        _json: bool = True
    ) -> bool:
        if _json:
            data = json.dumps(data)

        return await self.client.set(id, data, expire)

    async def close(self):
        await self.client.aclose(True)