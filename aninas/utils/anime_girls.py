from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..database import Redis
    from typing import Optional, List

import httpx

from .types.anime_girls import AnimeGirl

class AnimeGirls:
    def __init__(self, redis: Redis):
        self.client = httpx.AsyncClient(
            headers = {
                "User-Agent": "Aninas"
            }
        )

        self.redis = redis
        self.api_url = "https://api.ananas.moe/agac/v1"

    async def random(self) -> AnimeGirl:
        random = await self.client.get(f"{self.api_url}/random?metadata=true")
        json = random.json()

        return AnimeGirl(json)
    
    async def get(self, query: str) -> Optional[AnimeGirl]:
        cache = await self.redis.get(f"ag_{query}")

        if cache:
            return AnimeGirl(cache)
        
        data = await self.client.get(f"{self.api_url}/search?query={query}")
        json = data.json()

        if json == []:
            raise AnimeGirlsError("No anime girls found")
        
        result = json[0]

        await self.redis.set(f"ag_{result['name']}", result, 86400)

        return AnimeGirl(result)

    async def auto_comp(self, query: str) -> List[str]:
        items = []

        data = await self.client.get(f"{self.api_url}/search?query={query}")
        json = data.json()

        for item in json:
            items.append(item["name"])
        
        return items

class AnimeGirlsError(Exception):
    pass