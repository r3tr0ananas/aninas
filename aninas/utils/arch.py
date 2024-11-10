from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List

    from ..database import Redis

import httpx

from .types.arch import Package


class Arch:
    def __init__(self, redis: Redis):
        self.redis = redis
        self.client = httpx.AsyncClient(headers={"User-Agent": "Aninas"})

        self.base_aur = "https://aur.archlinux.org/rpc/v5"
        self.base_pacman = "https://archlinux.org/packages/"

    async def aur_search(self, query: str) -> List[str]:
        if not query:
            return []

        request = await self.client.get(f"{self.base_aur}/suggest/{query}")

        return request.json()

    async def aur(self, package: str) -> Package:
        cached = await self.redis.get(f"aur_{package}")

        if cached:
            return Package(cached["results"][0])

        request = await self.client.get(f"{self.base_aur}/info/{package}")
        response = request.json()

        if response["results"] == []:
            raise PackageNotFound("Package not found")

        await self.redis.set(f"aur_{package}", response, 60)

        return Package(response["results"][0])

    async def pacman_search(self, query: str) -> List[str]:
        if not query:
            return []

        package_names = []
        request = await self.client.get(f"{self.base_pacman}/search/json/?name={query}")

        items = request.json()["results"]

        for item in items:
            package_names.append(item["pkgname"])

        return package_names

    async def pacman(self, package: str) -> Package:
        cached = await self.redis.get(f"pacman_{package}")

        if cached:
            return Package(cached["results"][0], False)

        request = await self.client.get(
            f"{self.base_pacman}/search/json/?name={package}"
        )
        response = request.json()

        if response["results"] == []:
            raise PackageNotFound("Package not found")

        await self.redis.set(f"pacman_{package}", response, 60)

        return Package(response["results"][0], False)


class PackageNotFound(Exception):
    pass
