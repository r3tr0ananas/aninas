from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, List
    from .redis import Redis

import httpx

from ..constant import SATA_ANDAGI
from ..types.sata_andagi import SataAndagi

client = httpx.AsyncClient()

__all__ = (
    "get_random",
    "search",
    "autocomplete"
)

async def get_random() -> SataAndagi | str:
    try:
        request = await client.get(f"{SATA_ANDAGI}/random")
        data = request.json()
    except:
        return "Something went wrong"
        
    return SataAndagi(data)

async def search(query: str, redis: Redis) -> Optional[SataAndagi] | str:
    cache = await redis.get(query)

    if cache:
        return SataAndagi(cache)

    try:
        request = await client.get(f"{SATA_ANDAGI}/search?query={query}")
        data = request.json()
    except:
        return "Something went wrong"

    if data == []:
        return None
    
    await redis.set(query, data[0])

    return SataAndagi(data[0])

async def autocomplete(query: str) -> List[str]:
    comps = []

    try:
        request = await client.get(f"{SATA_ANDAGI}/search?query={query}")
        data = request.json()
    except:
        return "Something went wrong"

    for item in data:
        comps.append(item["title"]) 

    return comps