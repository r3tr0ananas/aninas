from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, List

import httpx

from ..constant import AGAC_URL
from ..types.agac import AGAC

client = httpx.AsyncClient()

async def get_random() -> AGAC:
    request = await client.get(f"{AGAC_URL}/random")
    id = request.headers.get("x-image-id")

    metadata = await client.get(f"{AGAC_URL}/get/{id}/metadata")
    metadata = AGAC(metadata.json())

    return metadata

async def search(query: str) -> Optional[AGAC]:
    request = await client.get(f"{AGAC_URL}/search?query={query}")
    data = request.json()

    if data == []:
        return None

    metadata = AGAC(data[0])

    return metadata

async def autocomplete(query: str) -> List[str]:
    comps = []

    request = await client.get(f"{AGAC_URL}/search?query={query}")

    for item in request.json():
        comps.append(item["name"])

    return comps
