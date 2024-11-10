from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..database import Redis
    from anmoku.resources.helpers import SearchResult


from anmoku import AsyncAnmoku, Anime, Character


class MAL:
    def __init__(self, redis: Redis):
        self.client = AsyncAnmoku()
        self.redis = redis

    async def search_anime(self, query: str) -> SearchResult[Anime]:
        return await self.client.search(Anime, query)

    async def search_character(self, query: str) -> SearchResult[Character]:
        return await self.client.search(Character, query)

    async def get_anime(self, id: int | str) -> Anime:
        redis_id = f"mal_{id}"
        cached = await self.redis.get(redis_id)

        if cached:
            return Anime(cached)

        anime = await self.client.get(Anime, id)

        await self.redis.set(redis_id, anime.data, 86400)

        return anime

    async def get_character(self, id: int | str) -> Character:
        redis_id = f"mal_{id}"
        cached = await self.redis.get(redis_id)

        if cached:
            return Character(cached)

        character = await self.client.get(Character, id)

        await self.redis.set(redis_id, character.data, 86400)

        return character
