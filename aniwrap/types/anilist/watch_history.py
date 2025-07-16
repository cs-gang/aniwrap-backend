"""Python objects to hold API responses from AniList."""

# Did NOT use pydantic here because running pydantic's validations
# on all the API responses would turn out to be expensive, with little gain.
# I feel like I can trust anilist's graphql API to give
# well-formed responses...
from typing import Literal

from attrs import define

# These class names mostly mirror the names of entities
# on the API
# See: https://docs.anilist.co/reference/

# Some of the attribute names obviously violate Python's naming conventions
# I don't care. I will not be bowing to the PEP-8 gods.


type SeasonType = Literal["WINTER", "SPRING", "SUMMER", "FALL"]


# TODO: need to recheck the types. which all are possibly null?
@define
class _SizedCoverImage:
    medium: str
    # can add the other sizes here if we need it


@define
class APIDate:
    year: int | None
    month: int | None
    day: int | None


@define
class AdvancedScore:
    # The API says people can score media like this
    # I've never seen this option in the UI
    # But I am fetching it for now.
    Story: int
    Characters: int
    Visuals: int
    Audio: int
    Enjoyment: int


@define
class _Title:
    userPreferred: str


@define
class Media:
    averageScore: int
    bannerImage: str
    coverImage: _SizedCoverImage
    description: str
    episodes: int | None
    genres: list[str]
    isAdult: bool
    isFavourite: bool
    meanScore: int
    season: SeasonType
    seasonYear: int
    siteUrl: str
    title: _Title
    type: Literal["ANIME", "MANGA"]


@define
class MediaList:
    advancedScores: AdvancedScore
    mediaId: int
    private: bool
    score: float
    startedAt: APIDate
    completedAt: APIDate
    repeat: int
    updatedAt: int  # TODO: is this a timestamp from epoch?
    status: str  # TODO: enum
    notes: str | None
    media: Media


@define
class MediaListGroup:
    name: str  # TODO: check if this can be an enum?
    status: str  # TODO: this can definitely be an enum
    entries: list[MediaList]  # these types are...poorly named
    # a MediaListGroup has an entries object, which is a list of MediaList? ok bro


@define
class MediaListCollection:
    lists: list[MediaListGroup]
    hasNextChunk: bool
