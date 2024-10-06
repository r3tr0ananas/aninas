import typing
from dataclasses import dataclass, field
from datetime import datetime

__all__ = ("TV",)

@dataclass
class TV:
    data: dict = field(repr=False)

    id: int = field(default=None)
    url: str = field(default=None)
    name: str = field(default=None)
    original_name: str = field(default=None)
    overview: str = field(default=None)
    image: str = field(default=None)
    genres: typing.List[str] = field(default=None)
    first_date: datetime = field(default=None)
    last_date: datetime = field(default=None)
    next_date: typing.Optional[datetime] = field(default=None)
    seasons: int = field(default=None)
    episodes: int = field(default=None)
    status: str = field(default=None)

    def __post_init__(self):
        self.id = self.data.get("id")
        self.url = f"https://www.themoviedb.org/tv/{self.id}"
        self.name = self.data.get("name")
        self.original_name = self.data.get("original_name")
        self.overview = self.data.get("overview")
        poster = self.data.get("poster_path")
        
        if poster is not None:
            self.image = "https://image.tmdb.org/t/p/w440_and_h660_face" + poster

        self.genres = [f"`{genre['name']}`" for genre in self.data.get("genres")]
        
        first_date = self.data.get("first_air_date")

        if first_date:
            self.first_date = datetime.strptime(first_date, "%Y-%m-%d")

            last_date = self.data.get("last_air_date")
            self.last_date = datetime.strptime(last_date, "%Y-%m-%d")

            next_date = self.data.get("next_episode_to_air", {}).get("air_date")

            if next_date is not None:
                self.next_date = datetime.strptime(next_date, "%Y-%m-%d")

        self.seasons = self.data.get("number_of_seasons")
        self.episodes = self.data.get("number_of_episodes")

        self.status = self.data.get("status")
