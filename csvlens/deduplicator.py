from typing import Iterator, List, Optional


class CSVDeduplicator:
    """
    Removes duplicate rows from a stream of CSV row dicts.

    Deduplication is performed lazily: only the set of seen keys is kept
    in memory, never the full row data (unless all columns are used as
    the key, which is the default).
    """

    def __init__(self, rows: Iterator[dict], keys: Optional[List[str]] = None):
        """
        Parameters
        ----------
        rows:
            Iterable of row dicts (e.g. from CSVReader or CSVQuery).
        keys:
            Column names used to determine uniqueness.  When *None* every
            column participates in the key (full-row dedup).
        """
        self._rows = rows
        self._keys = keys  # None means "all columns"

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def unique(self) -> List[dict]:
        """Return all unique rows as a list."""
        return list(self._iter_unique())

    def count(self) -> int:
        """Return the number of unique rows."""
        return sum(1 for _ in self._iter_unique())

    def duplicates(self) -> List[dict]:
        """
        Return every row that is a duplicate (i.e. a later occurrence of a
        key that was already seen).
        """
        seen: set = set()
        dupes: List[dict] = []
        for row in self._rows:
            key = self._make_key(row)
            if key in seen:
                dupes.append(row)
            else:
                seen.add(key)
        return dupes

    # ------------------------------------------------------------------
    # internals
    # ------------------------------------------------------------------

    def _make_key(self, row: dict):
        if self._keys is None:
            return tuple(sorted(row.items()))
        return tuple(row.get(k) for k in self._keys)

    def _iter_unique(self) -> Iterator[dict]:
        seen: set = set()
        for row in self._rows:
            key = self._make_key(row)
            if key not in seen:
                seen.add(key)
                yield row
