"""Query interface for filtering and aggregating CSV data."""

from typing import Iterable, Dict, Optional
from csvlens.reader import CSVReader
from csvlens.filter import RowFilter
from csvlens.aggregator import CSVAggregator


class CSVQuery:
    """Fluent query builder for CSV files."""

    def __init__(self, reader: CSVReader):
        self._reader = reader
        self._filters: list = []
        self._limit: Optional[int] = None
        self._skip: int = 0

    def where(self, column: str) -> "RowFilter":
        """Begin a filter expression on a column."""
        return RowFilter(self, column)

    def equals(self, column: str, value: str) -> "CSVQuery":
        """Filter rows where column equals value."""
        self._filters.append(("equals", column, value))
        return self

    def contains(self, column: str, value: str) -> "CSVQuery":
        """Filter rows where column contains value."""
        self._filters.append(("contains", column, value))
        return self

    def greater_than(self, column: str, value: float) -> "CSVQuery":
        """Filter rows where column is greater than numeric value."""
        self._filters.append(("gt", column, value))
        return self

    def less_than(self, column: str, value: float) -> "CSVQuery":
        """Filter rows where column is less than numeric value."""
        self._filters.append(("lt", column, value))
        return self

    def limit(self, n: int) -> "CSVQuery":
        """Limit results to n rows."""
        self._limit = n
        return self

    def skip(self, n: int) -> "CSVQuery":
        """Skip the first n rows."""
        self._skip = n
        return self

    def _apply_filters(self, row: Dict[str, str]) -> bool:
        for f in self._filters:
            op, col, val = f
            cell = row.get(col, "")
            if op == "equals" and cell != val:
                return False
            elif op == "contains" and val not in cell:
                return False
            elif op == "gt":
                try:
                    if float(cell) <= float(val):
                        return False
                except (ValueError, TypeError):
                    return False
            elif op == "lt":
                try:
                    if float(cell) >= float(val):
                        return False
                except (ValueError, TypeError):
                    return False
        return True

    def fetch(self) -> Iterable[Dict[str, str]]:
        """Execute query and return matching rows."""
        skipped = 0
        yielded = 0
        for row in self._reader:
            if not self._apply_filters(row):
                continue
            if skipped < self._skip:
                skipped += 1
                continue
            if self._limit is not None and yielded >= self._limit:
                break
            yield row
            yielded += 1

    def aggregate(self) -> CSVAggregator:
        """Return an aggregator over the current filtered result set."""
        return CSVAggregator(self.fetch())
