from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel


class AnilistConfig(BaseModel):
    client_id: int
    client_secret: str


class AniwrapConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_prefix="ANIWRAP_"
    )

    database_url: str
    anilist: AnilistConfig
