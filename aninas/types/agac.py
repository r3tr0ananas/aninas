from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List

from dataclasses import dataclass, field

__all__ = (
    "AGAC",
)
    
@dataclass
class AuthorsData:
    name: str = field(repr=False)
    github: str = field(repr=False)

@dataclass
class AGAC:
    data: dict = field(repr=False)  

    id: str = field(default=None)
    name: str = field(default=None)
    authors: List[AuthorsData] = field(default=None)
    category: str = field(default=None)
    tags: List[str] = field(default=None)
    sources: List[str] = field(default=None)

    def __post_init__(self):
        self.id = self.data.get("id")
        self.name = self.data.get("name")
        self.authors = [AuthorsData(user["name"], user["github"]) for user in self.data.get("authors", [])]
        self.category = self.data.get("category")
        self.tags = self.data.get("tags", [])
        self.sources = self.data.get("sources", [])