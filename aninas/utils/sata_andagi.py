from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, List

import httpx

from ..constant import SATA_ANDAGI
from ..types.sata_andagi import SataAndagi

client = httpx.AsyncClient()

__all__ = (
    "get_random",
    "search",
    "autocomplete"
)

async def get_random() -> SataAndagi:
    request = await client.get(f"{SATA_ANDAGI}/random")
    data = SataAndagi(request.json())

    return data

async def search(query: str) -> Optional[SataAndagi]:
    request = await client.get(f"{SATA_ANDAGI}/search?query={query}")
    data = request.json()

    if data == []:
        return None

    return SataAndagi(data[0])

async def autocomplete(query: str) -> List[str]:
    comps = []

    request = await client.get(f"{SATA_ANDAGI}/search?query={query}")

    for item in request.json():
        comps.append(item["title"]) 

    return comps