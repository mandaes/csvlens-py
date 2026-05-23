"""CSVSampler: randomly or deterministically sample rows from a CSV stream."""

from __future__ import annotations

import random
from typing import Iterable, Iterator, List, Optional


class CSVSampler:
    """Draw a sample of rows from an iterable of row dicts."""

    def __init__(self, rows: Iterable[dict], seed: Optional[int] = None) -> None:
        self._rows = rows
        self._rng = random.Random(seed)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def first(self, n: int) -> List[dict]:
        """Return the first *n* rows without loading the entire stream."""
        if n < 0:
            raise ValueError("n must be >= 0")
        result: List[dict] = []
        for row in self._rows:
            if len(result) >= n:
                break
            result.append(row)
        return result

    def reservoir(self, n: int) -> List[dict]:
        """Return a uniform random sample of *n* rows (reservoir sampling).

        The entire stream is consumed but only *n* rows are kept in memory
        at any given time once the reservoir is full.
        """
        if n < 0:
            raise ValueError("n must be >= 0")
        reservoir: List[dict] = []
        for i, row in enumerate(self._rows):
            if i < n:
                reservoir.append(row)
            else:
                j = self._rng.randint(0, i)
                if j < n:
                    reservoir[j] = row
        return reservoir

    def every_nth(self, n: int) -> Iterator[dict]:
        """Yield every *n*-th row (1-indexed), e.g. n=2 yields rows 1, 3, 5 …"""
        if n < 1:
            raise ValueError("n must be >= 1")
        for i, row in enumerate(self._rows):
            if i % n == 0:
                yield row

    def fraction(self, frac: float) -> List[dict]:
        """Return an approximate *frac* fraction of rows chosen randomly.

        Each row is independently included with probability *frac*.
        """
        if not 0.0 <= frac <= 1.0:
            raise ValueError("frac must be between 0.0 and 1.0")
        return [row for row in self._rows if self._rng.random() < frac]
