"""CSVProfiler: compute basic column-level statistics from a row iterable."""

from collections import defaultdict
from typing import Iterable


class CSVProfiler:
    """Compute lightweight column statistics without loading all data into memory.

    Statistics per column:
        - count       : number of non-empty values
        - null_count  : number of empty / missing values
        - unique      : approximate set of unique values (capped at *unique_cap*)
        - min / max   : lexicographic min and max of non-empty values
        - numeric     : True when every non-empty value is numeric
        - min_num / max_num / sum / mean : numeric aggregates (only when numeric=True)
    """

    def __init__(self, rows: Iterable[dict], unique_cap: int = 100):
        self._rows = rows
        self._unique_cap = unique_cap
        self._stats: dict | None = None

    def _compute(self) -> None:
        counts: dict[str, int] = defaultdict(int)
        null_counts: dict[str, int] = defaultdict(int)
        unique: dict[str, set] = defaultdict(set)
        mins: dict[str, str] = {}
        maxs: dict[str, str] = {}
        numeric_flag: dict[str, bool] = defaultdict(lambda: True)
        num_sum: dict[str, float] = defaultdict(float)
        num_min: dict[str, float] = {}
        num_max: dict[str, float] = {}

        for row in self._rows:
            for col, val in row.items():
                if val == "" or val is None:
                    null_counts[col] += 1
                    numeric_flag[col] = False
                    continue
                counts[col] += 1
                if len(unique[col]) < self._unique_cap:
                    unique[col].add(val)
                mins[col] = val if col not in mins else min(mins[col], val)
                maxs[col] = val if col not in maxs else max(maxs[col], val)
                if numeric_flag[col]:
                    try:
                        fval = float(val)
                        num_sum[col] += fval
                        num_min[col] = fval if col not in num_min else min(num_min[col], fval)
                        num_max[col] = fval if col not in num_max else max(num_max[col], fval)
                    except ValueError:
                        numeric_flag[col] = False

        all_cols = set(counts) | set(null_counts)
        self._stats = {}
        for col in all_cols:
            c = counts.get(col, 0)
            is_num = numeric_flag[col] and c > 0
            entry = {
                "count": c,
                "null_count": null_counts.get(col, 0),
                "unique": unique.get(col, set()),
                "min": mins.get(col),
                "max": maxs.get(col),
                "numeric": is_num,
            }
            if is_num:
                entry["sum"] = num_sum[col]
                entry["min_num"] = num_min.get(col)
                entry["max_num"] = num_max.get(col)
                entry["mean"] = num_sum[col] / c if c else None
            self._stats[col] = entry

    def profile(self) -> dict[str, dict]:
        """Return the full profile dict keyed by column name."""
        if self._stats is None:
            self._compute()
        return self._stats

    def column(self, name: str) -> dict:
        """Return statistics for a single column."""
        return self.profile()[name]
