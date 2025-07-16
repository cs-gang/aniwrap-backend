"""Service to fetch a user's watch history from AniList."""

from datetime import datetime
from logging import getLogger
from typing import Annotated

from aiohttp import ClientSession
from cattrs import structure
from fastapi import Depends

from aniwrap.config import AniwrapConfig, get_config
from aniwrap.misc import get_http_client
from aniwrap.types.anilist.watch_history import MediaListCollection

log = getLogger(__name__)


ANILIST_API_BASE_URL = "https://graphql.anilist.co"
ANILIST_MEDIALISTCOLLECTION_QUERY = """query ExampleQuery(
  $userName: String
  $type: MediaType
  $sort: [MediaListSort]
  $completedAtLesser: FuzzyDateInt
  $startedAtGreater: FuzzyDateInt
) {
  MediaListCollection(
    userName: $userName
    type: $type
    sort: $sort
    completedAt_lesser: $completedAtLesser
    startedAt_greater: $startedAtGreater
  ) {
    lists {
      name
      status
      entries {
        advancedScores
        mediaId
        private
        score
        startedAt {
          year
          month
          day
        }
        completedAt {
          year
          month
          day
        }
        status
        notes
        repeat
        updatedAt
        media {
          averageScore
          bannerImage
          coverImage {
            medium
          }
          description
          episodes
          genres
          isAdult
          isFavourite
          meanScore
          season
          seasonYear
          type
          siteUrl
          title {
            userPreferred
          }
        }
      }
    }
    hasNextChunk
  }
}
"""
ANILIST_MEDIALISTCOLLECTION_VARIABLES = {
    "userName": "",
    "type": "ANIME",
    "startedAtGreater": "",
    "completedAtLesser": "",
    "sort": "FINISHED_ON",
}


class AnilistWatchHistoryService:
    def __init__(
        self,
        config: Annotated[AniwrapConfig, Depends(get_config)],
        http: Annotated[ClientSession, Depends(get_http_client)],
    ) -> None:
        self.config = config
        self.http = http
        log.debug("Initialized AnilistWatchHistoryService")

    async def get_watch_history(
        self, username: str, lo: datetime | None = None, hi: datetime | None = None
    ) -> MediaListCollection:
        """Fetches the watch list for the specified user, in the given date range.

        Arguments:
            username: AniList username
            lo: lower bound of date range; defaults to the beginning of the current year
            hi: upper bound of date range; defaults to the end of the current year

        Returns:
            MediaListCollection
        """
        if lo is None:
            lo = datetime(datetime.today().year - 1, 12, 31)

        if hi is None:
            hi = datetime(datetime.today().year + 1, 1, 1)

        variables = {
            **ANILIST_MEDIALISTCOLLECTION_VARIABLES,
            "userName": username,
            "startedAtGreater": lo.strftime(r"%Y%m%d"),
            "completedAtLesser": hi.strftime(r"%Y%m%d"),
        }

        log.info(
            "Fetching Anilist watch history for %s; date range %s - %s",
            variables["userName"],
            variables["startedAtGreater"],
            variables["completedAtLesser"],
        )

        async with self.http.post(
            ANILIST_API_BASE_URL,
            json={"query": ANILIST_MEDIALISTCOLLECTION_QUERY, "variables": variables},
        ) as res:
            res.raise_for_status()
            raw = await res.json()
            log.info("Fetched AniList watch history for user %s", variables["userName"])

        obj = structure(raw["data"]["MediaListCollection"], MediaListCollection)
        if obj.hasNextChunk:
            log.warning(
                "API says there is more data left to be fetched for username %s, but we have stopped at one chunk",
                username,
            )
        return obj
