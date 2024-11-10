from __future__ import annotations

from dataclasses import dataclass, field

from .user import User

__all__ = ("Repository",)


@dataclass
class Repository:
    data: dict = field(repr=False)

    owner: User = field(default=None)

    name: str = field(default=None)
    description: str = field(default=None)
    url: str = field(default=None)
    stars: int = field(default=None)
    forks: int = field(default=None)
    watchers: int = field(default=None)
    created_at: str = field(default=None)
    updated_at: str = field(default=None)

    fork: bool = field(default=None)
    archived: bool = field(default=None)
    icon: str = field(default=None)

    def __post_init__(self):
        self.owner = User(self.data.get("owner"))

        self.name = self.data.get("name")
        self.description = self.data.get("description", "")
        self.url = self.data.get("html_url")
        self.stars = self.data.get("stars_count")
        self.forks = self.data.get("forks_count")
        self.watchers = self.data.get("watchers_count")
        self.created_at = self.data.get("created_at")
        self.updated_at = self.data.get("updated_at")

        self.fork = self.data.get("fork")
        self.archived = self.data.get("archived")
        self.icon = self.data.get("avatar_url")

        if self.icon == "":
            self.icon = self.owner.avatar
