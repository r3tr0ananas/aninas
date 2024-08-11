from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    ...

from dataclasses import dataclass, field

__all__ = (
    "SataAndagi",
)

@dataclass
class SataAndagi:
    data: dict = field(repr=False)  

    id: str = field(default=None)
    title: str = field(default=None)
    url: str = field(default=None)
    category: str = field(default=None)
    source: str = field(default=None)

    def __post_init__(self):
        self.id = self.data.get("id")
        self.title = self.data.get("title")
        self.url = self.data.get("url")
        self.category = self.data.get("category")
        self.source = self.data.get("source")