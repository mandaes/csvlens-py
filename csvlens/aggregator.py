"""Aggregation utilities for CSV data streams."""

from collections import defaultdict
from typing import Callable, Dict, Iterable, Optional


class CSVAggregator:
    """Performs aggregation operations over streamed CSV rows."""

    def __init__(self, rows: Iterable[Dict[str, str]]):
        self._rows = rows

    def count(self) -> int:
        """Return total number of rows."""
        return sum(1 for _ in self._rows)

    def count_by(self, column: str) -> Dict[str, int]:
        """Return counts grouped by unique values in a column."""
        counts: Dict[str, int] = defaultdict(int)
        for row in self._rows:
            key = row.get(column, "")
            counts[key] += 1
        return dict(counts)

    def sum(self, column: str) -> float:
        """Return the sum of numeric values in a column."""
        total = 0.0
        for row in self._rows:
            try:
                total += float(row.get(column, 0))
            except (ValueError, TypeError):
                pass
        return total

    def avg(self, column: str) -> Optional[float]:
        """Return the average of numeric values in a column."""
        total = 0.0
        count = 0
        for row in self._rows:
            try:
                total += float(row.get(column, 0))
                count += 1
            except (ValueError, TypeError):
                pass
        return total / count if count > 0 else None

    def min(self, column: str) -> Optional[float]:
        """Return the minimum numeric value in a column."""
        values = []
        for row in self._rows:
            try:
                values.append(float(row.get(column, 0)))
            except (ValueError, TypeError):
                pass
        return min(values) if values else None

    def max(self, column: str) -> Optional[float]:
        """Return the maximum numeric value in a column."""
        values = []
        for row in self._rows:
            try:
                values.append(float(row.get(column, 0)))
            except (ValueError, TypeError):
                pass
        return max(values) if values else None

    def unique(self, column: str) -> list:
        """Return sorted list of unique values in a column."""
        seen = set()
        for row in self._rows:
            seen.add(row.get(column, ""))
        return sorted(seen)
