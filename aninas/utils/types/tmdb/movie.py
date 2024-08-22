import typing

from datetime import datetime
from dataclasses import dataclass, field

__all__ = ("Movie",)

@dataclass
class Movie:
    data: dict = field(repr=False)

    id: int = field(default=None)
    url: str = field(default=None)
    name: str = field(default=None)
    original_name: str = field(default=None)
    overview: str = field(default=None)
    image: str = field(default=None)
    genre: typing.List[str] = field(default=None)
    genres: list[str] = field(default=None)
    date: datetime = field(default=None)
    status: str = field(default=None)

    def __post_init__(self):
        self.id = self.data.get("id")
        self.url = f"https://www.themoviedb.org/movie/{self.id}"
        self.name = self.data.get("title")
        self.original_name = self.data.get("original_title")
        self.overview = self.data.get("overview")
        self.image = "https://cdn.ananas.moe/not-found.png"

        poster = self.data.get("poster_path")
        
        if poster is not None:
            self.image = "https://image.tmdb.org/t/p/w440_and_h660_face" + poster

        self.genres = [f"`{genre['name']}`" for genre in self.data.get("genres")]
        
        date = self.data.get("release_date")

        if date:
            self.date = datetime.strptime(date, "%Y-%m-%d")

        self.status = self.data.get("status")