from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query

from aniwrap.service.stats import StatisticsService
from aniwrap.service.watch_history.anilist import AnilistWatchHistoryService
from aniwrap.types.dto import CalculatedStats

router = APIRouter(prefix="/wrapped")


Provider = Literal["mal", "anilist"]


@router.get("/")
async def get_wrapped(
    provider: Annotated[Provider, Query(description="The anime tracking provider")],
    username: Annotated[
        str, Query(description="The user's username on the specified platform")
    ],
    watch_history_service: Annotated[AnilistWatchHistoryService, Depends()],
    stats: Annotated[StatisticsService, Depends()],
) -> CalculatedStats:
    data = await watch_history_service.get_watch_history(username=username)
    df = stats.make_dataframe_from_anilist(data)
    return stats.calculate_stats(df)
