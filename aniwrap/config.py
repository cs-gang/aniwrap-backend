from functools import cache
from logging import getLogger

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

log = getLogger(__name__)


class AnilistConfig(BaseModel):
    client_id: int
    client_secret: str


class AniwrapConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_prefix="ANIWRAP_"
    )

    database_url: str
    anilist: AnilistConfig


@cache
def get_config() -> AniwrapConfig:
    log.info("Fetching configuration settings")
    return AniwrapConfig()  # type: ignore
