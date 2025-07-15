from logging import getLogger
from typing import Any

import duckdb
import polars as pl
from cattrs import unstructure

from aniwrap.types.anilist.watch_history import MediaListCollection
from aniwrap.types.dto import CalculatedStats

log = getLogger(__name__)


class StatisticsService:
    @staticmethod
    def _flatten_anilist_data(data: MediaListCollection) -> list[dict[str, Any]]:
        rows = []

        # TODO: implement date parsing
        for watch_list in data.lists:
            base_row = {"list_name": watch_list.name, "status": watch_list.status}
            for entry in watch_list.entries:
                entry_dict: dict = unstructure(entry)

                media_dict = entry_dict.pop("media")
                rows.append({**base_row, **entry_dict, **media_dict})

        return rows

    def make_dataframe_from_anilist(self, data: MediaListCollection) -> pl.DataFrame:
        return pl.from_dicts(self._flatten_anilist_data(data))

    def calculate_stats(self, df: pl.DataFrame) -> CalculatedStats:
        total_count = duckdb.sql("SELECT COUNT(*) as cnt FROM df").fetchone()
        n = total_count[0] if total_count else 0

        # I am not exactly certain that only these three statuses exist
        # which is why I ran another query for the total anime
        totals: list[tuple[str, int]] = duckdb.sql(
            "SELECT status, COUNT(*) as cnt FROM df GROUP BY status"
        ).fetchall()
        n_completed, n_ongoing, n_dropped = 0, 0, 0
        for status, n in totals:
            match status:
                case "CURRENT":
                    n_ongoing = n
                case "DROPPED":
                    n_dropped = n
                case "COMPLETED":
                    n_completed = n
                case _:
                    log.warning(
                        f"Got unexpected value for 'status' while calculating totals: {status} = {n}"
                    )

        episodes_res = duckdb.sql(
            "SELECT SUM(episodes) FROM df WHERE status = 'COMPLETED'"
        ).fetchone()
        n_episodes = episodes_res[0] if episodes_res else 0

        return CalculatedStats(
            n=n,
            n_completed=n_completed,
            n_dropped=n_dropped,
            n_ongoing=n_ongoing,
            n_episodes=n_episodes,
            anime={},
        )
