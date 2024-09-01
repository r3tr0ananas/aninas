from dataclasses import dataclass, field

__all__ = ("Person",)

GENDER = {
    0: "Not specified",
    1: "Female",
    2: "Male",
    3: "Non-binary"
}

@dataclass
class Person:
    data: dict = field(repr=False)

    id: int = field(default=None)
    bio: str = field(default=None)
    url: str = field(default=None)
    name: str = field(default=None)
    original_name: str = field(default=None)
    gender: str = field(default=None)
    image: str = field(default=None)

    def __post_init__(self):
        self.id = self.data.get("id")
        self.bio = self.data.get("biography")
        self.url = f"https://www.themoviedb.org/person/{self.id}"
        self.name = self.data.get("name")
        self.original_name = self.data.get("original_name")
        self.gender = GENDER[self.data.get("gender")]
        self.image = "https://image.tmdb.org/t/p/w440_and_h660_face" + self.data.get("profile_path")