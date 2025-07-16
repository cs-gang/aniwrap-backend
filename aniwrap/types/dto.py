from datetime import date
from typing import Literal, TypedDict

from pydantic import BaseModel


class _MediaAndDate(TypedDict):
    media_id: str
    completed_at: date


class _GenreCounts(TypedDict):
    genre: str
    genre_count: int


class AnimeData(BaseModel):
    media_id: int
    title: str
    banner_url: str
    cover_url: str
    description: str
    average_score: int
    mean_score: int
    episodes: int | None
    genres: list[str]
    season: Literal["WINTER", "SPRING", "SUMMER", "FALL"]
    season_year: int
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
    avg_score: float
    scores_valid: bool
    first_completed: _MediaAndDate | None
    last_completed: _MediaAndDate | None

    genre_counts: list[_GenreCounts]

    anime: dict[int, AnimeData]
