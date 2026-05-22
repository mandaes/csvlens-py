"""Fluent query interface for chaining filters and projections on a CSVReader."""

from typing import Iterator, Dict, List, Optional, Callable
from csvlens.filter import RowFilter


class CSVQuery:
    """Chainable, lazy query builder on top of a CSVReader."""

    def __init__(self, reader):
        """
        Args:
            reader: A CSVReader instance providing an iterable of row dicts.
        """
        self._reader = reader
        self._filters: List[RowFilter] = []
        self._columns: Optional[List[str]] = None
        self._limit: Optional[int] = None

    def where(self, predicate: Callable[[Dict[str, str]], bool]) -> "CSVQuery":
        """Add a custom filter predicate."""
        self._filters.append(RowFilter(predicate))
        return self

    def equals(self, column: str, value: str) -> "CSVQuery":
        """Filter rows where column equals value."""
        self._filters.append(RowFilter.equals(column, value))
        return self

    def contains(self, column: str, substring: str) -> "CSVQuery":
        """Filter rows where column contains substring."""
        self._filters.append(RowFilter.contains(column, substring))
        return self

    def greater_than(self, column: str, value: float) -> "CSVQuery":
        """Filter rows where column (numeric) > value."""
        self._filters.append(RowFilter.greater_than(column, value))
        return self

    def less_than(self, column: str, value: float) -> "CSVQuery":
        """Filter rows where column (numeric) < value."""
        self._filters.append(RowFilter.less_than(column, value))
        return self

    def select(self, *columns: str) -> "CSVQuery":
        """Project only the specified columns in results."""
        self._columns = list(columns)
        return self

    def limit(self, n: int) -> "CSVQuery":
        """Limit the number of rows returned."""
        self._limit = n
        return self

    def _iter_rows(self) -> Iterator[Dict[str, str]]:
        rows = iter(self._reader)
        if self._filters:
            combined = RowFilter.combine(*self._filters)
            rows = combined.apply(rows)
        if self._limit is not None:
            rows = _take(rows, self._limit)
        if self._columns is not None:
            cols = self._columns
            rows = ({c: row[c] for c in cols if c in row} for row in rows)
        return rows

    def __iter__(self) -> Iterator[Dict[str, str]]:
        return self._iter_rows()

    def to_list(self) -> List[Dict[str, str]]:
        """Materialise all matching rows into a list."""
        return list(self._iter_rows())

    def count(self) -> int:
        """Count matching rows without materialising full dicts."""
        return sum(1 for _ in self._iter_rows())


def _take(iterator: Iterator, n: int) -> Iterator:
    for i, item in enumerate(iterator):
        if i >= n:
            break
        yield item
