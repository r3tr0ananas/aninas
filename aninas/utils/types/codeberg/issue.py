from __future__ import annotations

import typing
from dataclasses import dataclass, field

from .user import User

__all__ = ("Issue",)

@dataclass
class Issue:
    data: dict = field(repr=False)

    owner: User = field(default=None)

    id: int = field(default=None)
    type: str = field(default=None)
    title: str = field(default=None)
    body: str = field(default=None)
    labels: typing.List[str] = field(default=None)
    state: str = field(default=None)
    created_at: str = field(default=None)
    html_url: str = field(default=None)
    due_date: str = field(default=None)
    milestone: str = field(default=None)
    assginees: typing.List[User] = field(default=None)
    image: str = field(default=None)

    merged: bool = field(default=None)
    draft: bool = field(default=None)
    requsted_reviewers: typing.List[User] = field(default=None)

    full_name: str = field(default=None)

    def __post_init__(self):
        self.owner = User(self.data.get("user", {}))

        self.id = self.data.get("number")
        self.type = self.data.get("html_url").split("/")[5]
        self.title = self.data.get("title")
        self.body = self.data.get("body")
        self.labels = [f"`{label['name']}`" for label in self.data.get("labels")]
        self.state = self.data.get("state")
        self.created_at = self.data.get("created_at")
        self.html_url = self.data.get("html_url")
        self.due_date = self.data.get("due_date")
        milestone = self.data.get("milestone")
        assginees = self.data.get("assignees")
        assets = self.data.get("assets")

        if milestone is not None:
            self.milestone = milestone.get("title")

        if assginees is not None:
            self.assginees = [User(user) for user in assginees]
        
        if assets is not None:
            for asset in assets:
                file_ext = asset["name"].split(".")[-1]

                if file_ext in ["png", "jpeg", "jpg"]:
                    self.image = asset["browser_download_url"]
                    
                    break

        self.full_name = self.data.get("repository").get("full_name")

        pr_data = self.data.get("pr")

        if pr_data is not None:
            self.requsted_reviewers = pr_data.get("requested_reviewers", [])

            if self.requsted_reviewers is not None:
                self.requsted_reviewers = [User(user) for user in self.requsted_reviewers]

            self.merged = pr_data.get("merged")
            self.draft = pr_data.get("draft")
