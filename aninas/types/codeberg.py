from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List

from dataclasses import dataclass, field

__all__ = (
    "CodebergRepo",
    "CodebergOrg",
    "CodebergUser",
)

@dataclass
class CodebergRepo:
    data: dict = field(repr=False)  

    owner: CodebergUser = field(default=None)
    
    name: str = field(default=None)
    description: str = field(default=None)
    url: str = field(default=None)
    stars: int = field(default=None)
    forks: int = field(default=None)
    created_at: str = field(default=None)
    updated_at: str = field(default=None)

    def __post_init__(self):
        self.owner = CodebergUser(self.data.get("owner", {}))

        self.name = self.data.get("name")
        self.description = self.data.get("description", "")
        self.url = self.data.get("html_url")
        self.stars = self.data.get("stars_count")
        self.forks = self.data.get("forks_count")
        self.created_at = self.data.get("created_at")
        self.updated_at = self.data.get("updated_at")

@dataclass
class CodebergOrg:
    data: dict = field(repr=False)

    username: str = field(default=None)
    full_name: str = field(default=None)
    avatar: str = field(default=None)
    location: str = field(default=None)
    website: str = field(default=None)
    description: str = field(default=None)
    user_url: str = field(default=None)

    def __post_init__(self):
        self.username = self.data.get("username")
        self.full_name = self.data.get("full_name")
        self.avatar = self.data.get("avatar_url")
        self.location = self.data.get("html_url")
        self.website = self.data.get("username")
        self.description = self.data.get("avatar_url")
        self.user_url = "https://codeberg.org/" + self.username

@dataclass
class CodebergUser:
    data: dict = field(repr=False)
    orgs: dict = field(repr=False, default=None)

    username: str = field(default=None)
    full_name: str = field(default=None)
    user_url: str = field(default=None)
    avatar: str = field(default=None)
    created: str = field(default=None)
    location: str = field(default=None)
    website: str = field(default=None)
    description: str = field(default=None)
    followers: int = field(default=None)
    following: int = field(default=None)
    starred_repos: int = field(default=None)
    joined_orgs: List[CodebergOrg] = field(default=None)

    def __post_init__(self):
        self.username = self.data.get("username")
        self.full_name = self.data.get("full_name")
        self.user_url = "https://codeberg.org/" + self.username
        self.avatar = self.data.get("avatar_url")
        self.created = self.data.get("created")
        self.location = self.data.get("location")
        self.website = self.data.get("website")
        self.description = self.data.get("description")
        self.followers = self.data.get("followers_count")
        self.following = self.data.get("following_count")
        self.starred_repos = self.data.get("starred_repos_count")
        if self.orgs is not None:
            self.joined_orgs = [CodebergOrg(org) for org in self.orgs]