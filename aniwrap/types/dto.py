from pydantic import BaseModel


class AnimeData(BaseModel):
    media_id: str
    title: str
    banner_url: str
    thumbnail_url: str


class CalculatedStats(BaseModel):
    n_completed: int
    n_ongoing: int
    n_dropped: int

    anime: dict[str, AnimeData]
