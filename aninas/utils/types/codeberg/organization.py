from dataclasses import dataclass, field

__all__ = ("Organization",)

@dataclass
class Organization:
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
