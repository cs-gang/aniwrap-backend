from pydantic import BaseModel


class AnimeData(BaseModel):
    media_id: str
    title: str
    banner_url: str
    thumbnail_url: str


class CalculatedStats(BaseModel):
    n: int
    n_completed: int
    n_ongoing: int
    n_dropped: int
    n_episodes: int

    anime: dict[str, AnimeData]
