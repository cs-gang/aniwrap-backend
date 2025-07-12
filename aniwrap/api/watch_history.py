from typing import Annotated, Literal

from cattrs import unstructure
from fastapi import APIRouter, Depends, Path

from aniwrap.service.watch_history.anilist import AnilistWatchHistoryService

router = APIRouter(prefix="/watched")


Provider = Literal["mal", "anilist"]


@router.get("/{provider}/{username}")
async def get_watch_history(
    provider: Annotated[Provider, Path(description="The anime tracking provider")],
    username: Annotated[
        str, Path(description="The user's username on the specified platform")
    ],
    watch_history_service: Annotated[AnilistWatchHistoryService, Depends()],
) -> dict:
    o = await watch_history_service.get_watch_history(username)
    return unstructure(o)
