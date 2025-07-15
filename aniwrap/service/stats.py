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

        return CalculatedStats(
            n_completed=n_completed, n_dropped=n_dropped, n_ongoing=n_ongoing, anime={}
        )
