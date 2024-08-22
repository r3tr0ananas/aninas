from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..database import Redis
    from typing import Optional, List

import httpx

from ..constant import TMDB_KEY

from .types.tmdb.search import Search

from .types.tmdb.person import Person
from .types.tmdb.movie import Movie
from .types.tmdb.tv import TV

class TMDb:
    def __init__(self, redis: Redis):
        self.client = httpx.AsyncClient(
            headers = {
                "User-Agent": "Aninas"
            }
        )

        self.redis = redis
        self.api_url = "https://api.themoviedb.org/3"
    
    async def get(self, result: tuple) -> Optional[Person | Movie | TV]:
        id = result[0]
        type = result[1]

        details = await self.redis.get(f"tmdb_{type}_{id}")

        if details is None:
            details = await self.client.get(f"{self.api_url}/{type}/{id}?api_key={TMDB_KEY}")
            details = details.json()

            await self.redis.set(f"tmdb_{type}_{id}", details, 86400)

        if type == "movie":
            return Movie(details)
        elif type == "tv":
            return TV(details)

        return Person(details)
    
    async def search(self, query: str) -> Optional[List[Search]]:
        request = await self.client.get(f"{self.api_url}/search/multi?query={query}&api_key={TMDB_KEY}")
        json = request.json()

        results = json["results"]

        if results == []:
            raise TMDbError("No results")
    
        items = []

        for result in results:
            image = result.get("poster_path") or result.get("profile_path")

            if image is None:
                continue

            id = result.get("id")
            type = result.get("media_type")
            name = result.get("name") or result.get("title")
            description = result.get("overview")

            if type == "person":
                department = result.get("known_for_department")

                description = f"Known for {department}"

            items.append(
                {
                    "id": id, 
                    "type": type, 
                    "name": name, 
                    "description": description
                }
            )

        return items

    async def auto_comp(self, query: str) -> List[str]:
        comps = []
        request = await self.client.get(f"{self.api_url}/search/multi?query={query}&api_key={TMDB_KEY}")
        json = request.json()

        results = json["results"]

        for result in results:
            name = result.get("name")
            image = result.get("poster_path") or result.get("profile_path")

            if name is None:
                name = result.get("title")
            
            if image is None:
                continue

            comps.append(name)
        
        return comps

    
class TMDbError(Exception):
    pass