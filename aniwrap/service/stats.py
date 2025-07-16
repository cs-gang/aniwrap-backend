from datetime import date
from logging import getLogger
from typing import Any, TypedDict

import duckdb
import polars as pl
from cattrs import unstructure

from aniwrap.types.anilist.watch_history import MediaListCollection
from aniwrap.types.dto import AnimeData, CalculatedStats, _MediaAndDate

log = getLogger(__name__)


DateDict = TypedDict("DateDict", {"year": int, "month": int, "day": int})


def _to_date(d: DateDict) -> date | None:
    if None in d.values():
        return None
    return date(**d)


class StatisticsService:
    @staticmethod
    def _flatten_anilist_data(data: MediaListCollection) -> list[dict[str, Any]]:
        rows = []

        for watch_list in data.lists:
            base_row = {"list_name": watch_list.name, "status": watch_list.status}
            for entry in watch_list.entries:
                entry_dict: dict = unstructure(entry)

                entry_dict["startedAt"] = _to_date(entry_dict["startedAt"])
                entry_dict["completedAt"] = _to_date(entry_dict["completedAt"])

                media_dict = entry_dict.pop("media")
                rows.append({**base_row, **entry_dict, **media_dict})

        return rows

    def make_dataframe_from_anilist(self, data: MediaListCollection) -> pl.DataFrame:
        return pl.from_dicts(self._flatten_anilist_data(data))

    def calculate_stats(self, df: pl.DataFrame) -> CalculatedStats:
        # I've made individual functions for each calculation and delegated to them
        # otherwise this function would be too long.
        media = self._get_media(df)
        n, n_completed, n_ongoing, n_dropped = self._get_counts(df)
        n_episodes = self._get_episodes_watched_count(df)
        first_completed = self._get_first_completed(df)
        last_completed = self._get_last_completed(df)
        scores_valid = self._get_scores_validity(df)
        average_score = self._get_average_score(df)

        return CalculatedStats(
            n=n,
            n_completed=n_completed,
            n_dropped=n_dropped,
            n_ongoing=n_ongoing,
            n_episodes=n_episodes,
            avg_score=average_score,
            scores_valid=scores_valid,
            first_completed=first_completed,
            last_completed=last_completed,
            anime={obj["media_id"]: AnimeData.model_validate(obj) for obj in media},
        )

    def _get_first_completed(self, df: pl.DataFrame) -> _MediaAndDate | None:
        first_completed_rel = duckdb.sql(
            "SELECT mediaId::VARCHAR AS media_id, completedAt FROM df "
            "WHERE DATE_PART('year', completedAt) = DATE_PART('year', NOW()) "
            "ORDER BY completedAt LIMIT 1"
        ).fetchone()
        if first_completed_rel:
            return _MediaAndDate(
                {
                    "media_id": first_completed_rel[0],
                    "completed_at": first_completed_rel[1],
                }
            )

    def _get_average_score(self, df: pl.DataFrame) -> float:
        res = duckdb.sql(
            "SELECT AVG(score)::DOUBLE FROM df "
            "WHERE status = 'COMPLETED' AND score != 0 AND score IS NOT NULL"
        ).fetchone()
        if res and res[0]:
            return res[0]
        else:
            log.warning(
                f"Average score query did NOT return a result: {res}; defaulting to 0"
            )
            return 0.0

    def _get_scores_validity(self, df: pl.DataFrame) -> bool:
        # Some users just don't put scores for the anime they watch
        # In which case, doing any computation based on the score field
        # would be meaningless
        # If this function returns true, consider any stats calculated
        # based on the score field to be VALID.

        ENTRIES_SCORED_THRESHOLD = 0.5
        res = duckdb.sql(
            "SELECT "
            "AVG(CASE WHEN score = 0 OR score IS NULL THEN 0 ELSE 1 END) AS fraction_non_zero_scores "
            "FROM df "
            "WHERE status = 'COMPLETED'"  # people will only score anime they've completed, right?
        ).fetchone()
        if res:
            return res[0] >= ENTRIES_SCORED_THRESHOLD
        else:
            log.warning(
                "Score validity query did NOT return a result; defaulting to scores being valid."
            )
            return True

    def _get_last_completed(self, df: pl.DataFrame) -> _MediaAndDate | None:
        last_completed_rel = duckdb.sql(
            "SELECT mediaId::VARCHAR, completedAt FROM df "
            "WHERE DATE_PART('year', completedAt) = DATE_PART('year', NOW()) "
            "ORDER BY completedAt DESC LIMIT 1"
        ).fetchone()
        if last_completed_rel:
            return _MediaAndDate(
                {
                    "media_id": last_completed_rel[0],
                    "completed_at": last_completed_rel[1],
                }
            )

    def _get_counts(self, df: pl.DataFrame) -> tuple[int, int, int, int]:
        total_count = duckdb.sql("SELECT COUNT(*) as cnt FROM df").fetchone()
        n = total_count[0] if total_count else 0

        # I am not exactly certain that only these three statuses exist
        # which is why I ran another query for the total anime
        totals: list[tuple[str, int]] = duckdb.sql(
            "SELECT status, COUNT(*) as cnt FROM df GROUP BY status"
        ).fetchall()
        n_completed, n_ongoing, n_dropped = 0, 0, 0
        for status, count in totals:
            match status:
                case "CURRENT":
                    n_ongoing = count
                case "DROPPED":
                    n_dropped = count
                case "COMPLETED":
                    n_completed = count
                case _:
                    log.warning(
                        f"Got unexpected value for 'status' while calculating totals: {status} = {count}"
                    )

        return n, n_completed, n_ongoing, n_dropped

    def _get_episodes_watched_count(self, df: pl.DataFrame) -> int:
        episodes_rel = duckdb.sql(
            "SELECT SUM(episodes) FROM df WHERE status = 'COMPLETED'"
        ).fetchone()
        return episodes_rel[0] if episodes_rel else 0

    def _get_media(self, df: pl.DataFrame) -> list[dict[str, Any]]:
        return (
            duckdb.sql(
                "SELECT "
                " DISTINCT mediaId AS media_id,"
                " title.userPreferred AS title,"
                " bannerImage AS banner_url,"
                " coverImage.medium AS cover_url,"
                " description, "
                " averageScore AS average_score,"
                " meanScore AS mean_score,"
                " episodes,"
                " genres,"
                " season,"
                " seasonYear AS season_year,"
                " siteUrl AS site_url,"
                " isAdult AS is_adult,"
                " isFavourite AS is_favourite,"
                " type "
                "FROM df"
            )
            .pl()
            .to_dicts()
        )
