"""Lazy row filtering for CSVReader using predicate functions or column comparisons."""

from typing import Callable, Any, Iterator, Dict, Optional


class RowFilter:
    """Applies lazy filter predicates to streamed CSV rows."""

    def __init__(self, predicate: Callable[[Dict[str, str]], bool]):
        """
        Args:
            predicate: A callable that receives a row dict and returns True to keep the row.
        """
        self._predicate = predicate

    def apply(self, rows: Iterator[Dict[str, str]]) -> Iterator[Dict[str, str]]:
        """Lazily yield rows that satisfy the predicate."""
        for row in rows:
            if self._predicate(row):
                yield row

    @classmethod
    def equals(cls, column: str, value: str) -> "RowFilter":
        """Filter rows where column value equals the given string."""
        return cls(lambda row: row.get(column) == value)

    @classmethod
    def contains(cls, column: str, substring: str) -> "RowFilter":
        """Filter rows where column value contains the given substring."""
        return cls(lambda row: substring in row.get(column, ""))

    @classmethod
    def greater_than(cls, column: str, value: float) -> "RowFilter":
        """Filter rows where column value (numeric) is greater than value."""
        def predicate(row: Dict[str, str]) -> bool:
            try:
                return float(row.get(column, "")) > value
            except (ValueError, TypeError):
                return False
        return cls(predicate)

    @classmethod
    def less_than(cls, column: str, value: float) -> "RowFilter":
        """Filter rows where column value (numeric) is less than value."""
        def predicate(row: Dict[str, str]) -> bool:
            try:
                return float(row.get(column, "")) < value
            except (ValueError, TypeError):
                return False
        return cls(predicate)

    @classmethod
    def combine(cls, *filters: "RowFilter") -> "RowFilter":
        """Combine multiple filters with logical AND."""
        def predicate(row: Dict[str, str]) -> bool:
            return all(f._predicate(row) for f in filters)
        return cls(predicate)
