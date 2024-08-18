from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List

from dataclasses import dataclass, field

@dataclass
class AuthorsData:
    name: str = field(default=False)
    github: str = field(default=False)

@dataclass
class AnimeGirl:
    data: dict = field(repr=False)  

    id: str = field(default=None)
    name: str = field(default=None)
    image: str = field(default=None)
    authors: List[AuthorsData] = field(default=None)
    category: str = field(default=None)
    tags: List[str] = field(default=None)
    sources: List[str] = field(default=None)

    def __post_init__(self):
        self.id = self.data.get("id")
        self.name = self.data.get("name")
        self.image = f"https://api.ananas.moe/agac/v1/get/" + self.data.get("id")
        self.authors = [AuthorsData(user["name"], user["github"]) for user in self.data.get("authors", [])]
        self.category = self.data.get("category")
        self.tags = self.data.get("tags", [])
        self.sources = self.data.get("sources", [])