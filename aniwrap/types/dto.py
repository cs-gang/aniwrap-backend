from typing import Literal

from pydantic import BaseModel


class AnimeData(BaseModel):
    media_id: str
    title: str
    banner_url: str
    cover_url: str
    average_score: int
    mean_score: int
    episodes: int
    genres: list[str]
    season: Literal["WINTER", "SPRING", "SUMMER", "FALL"]
    site_url: str
    is_adult: bool
    is_favourite: bool
    type: Literal["ANIME", "MANGA"]


class CalculatedStats(BaseModel):
    n: int
    n_completed: int
    n_ongoing: int
    n_dropped: int
    n_episodes: int

    anime: dict[str, AnimeData]
