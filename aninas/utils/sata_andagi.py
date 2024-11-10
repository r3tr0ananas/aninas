from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..database import Redis
    from typing import Optional, List

import httpx


class SataAndagi:
    def __init__(self, redis: Redis):
        self.client = httpx.AsyncClient(headers={"User-Agent": "Aninas"})

        self.redis = redis
        self.api_url = "https://sata-andagi.moe/api"

    async def random(self) -> str:
        request = await self.client.get(f"{self.api_url}/random")

        return request.json()["url"]

    async def get(self, query: str) -> Optional[str]:
        cache = await self.redis.get(f"andagi_{query}")

        if cache:
            return cache["url"]

        request = await self.client.get(f"{self.api_url}/search?query={query}")
        json = request.json()

        if json == []:
            raise SataAndagiError("No results found")

        result = json[0]

        await self.redis.set(f"andagi_{result['title']}", result, 86400)

        return result["url"]

    async def auto_comp(self, search: str) -> List[str]:
        items = []

        request = await self.client.get(f"{self.api_url}/search?query={search}")
        json = request.json()

        for item in json:
            items.append(item["title"])

        return items


class SataAndagiError(Exception):
    pass
