from __future__ import annotations

import typing
from dataclasses import dataclass, field

from .organization import Organization

__all__ = ("User",)


@dataclass
class User:
    data: dict = field(repr=False)

    username: str = field(default=None)
    full_name: str = field(default=None)
    user_url: str = field(default=None)
    avatar: str = field(default=None)
    pronouns: str = field(default=None)
    created: str = field(default=None)
    location: str = field(default=None)
    website: str = field(default=None)
    description: str = field(default=None)
    followers: int = field(default=None)
    following: int = field(default=None)
    starred_repos: int = field(default=None)

    repositories: dict = field(default=None)
    organizations: typing.List[Organization] = field(default=None)

    def __post_init__(self):
        self.username = self.data.get("username")
        self.full_name = self.data.get("full_name")
        self.user_url = "https://codeberg.org/" + self.username
        self.avatar = self.data.get("avatar_url")
        self.pronouns = self.data.get("pronouns")
        self.created = self.data.get("created")
        self.location = self.data.get("location")
        self.website = self.data.get("website")
        self.description = self.data.get("description")
        self.followers = self.data.get("followers_count")
        self.following = self.data.get("following_count")
        self.starred_repos = self.data.get("starred_repos_count")

        repositories = self.data.get("repos")
        organizations = self.data.get("orgs")

        if repositories is not None:
            self.repositories = repositories

        if organizations is not None:
            self.organizations = [Organization(org) for org in organizations]
