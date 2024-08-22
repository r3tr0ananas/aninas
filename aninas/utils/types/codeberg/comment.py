from dataclasses import dataclass, field

from .user import User
from .issue import Issue

__all__ = ("Comment",)

@dataclass
class Comment:
    data: dict = field(repr=False)

    owner: User = field(default=None)
    issue: Issue = field(default=None)

    body: str = field(default=None)
    created_at: str = field(default=None)
    html_url: str = field(default=None)

    def __post_init__(self):
        self.owner = User(self.data.get("user"))
        self.issue = Issue(self.data.get("issue"))

        self.body = self.data.get("body")
        self.created_at = self.data.get("created_at")
        self.html_url = self.data.get("html_url")