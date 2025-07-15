from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Path

from aniwrap.service.stats import StatisticsService
from aniwrap.service.watch_history.anilist import AnilistWatchHistoryService
from aniwrap.types.dto import CalculatedStats

router = APIRouter(prefix="/wrapped")


Provider = Literal["mal", "anilist"]


@router.get("/{provider}/{username}")
async def get_wrapped(
    provider: Annotated[Provider, Path(description="The anime tracking provider")],
    username: Annotated[
        str, Path(description="The user's username on the specified platform")
    ],
    watch_history_service: Annotated[AnilistWatchHistoryService, Depends()],
    ss: Annotated[StatisticsService, Depends()],
) -> CalculatedStats:
    data = await watch_history_service.get_watch_history(username=username)
    df = ss.make_dataframe_from_anilist(data)
    return ss.calculate_stats(df)
