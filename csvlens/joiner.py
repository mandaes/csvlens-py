"""CSVJoiner: join two streams of rows on a common key."""
from typing import Iterable, Iterator, Dict, Any, Optional


class CSVJoiner:
    """Perform an in-memory hash join between two row iterables on a shared key.

    The *left* side is streamed lazily; the *right* side is fully buffered so
    that lookups are O(1).  This is intentional — right-side data sets should
    be small enough to fit in memory (lookup tables, dimension tables, etc.).
    """

    def __init__(
        self,
        left: Iterable[Dict[str, Any]],
        right: Iterable[Dict[str, Any]],
        on: str,
        how: str = "inner",
        right_prefix: str = "right_",
    ) -> None:
        if how not in ("inner", "left"):
            raise ValueError(f"Unsupported join type: {how!r}. Use 'inner' or 'left'.")
        self._left = left
        self._right = right
        self._on = on
        self._how = how
        self._right_prefix = right_prefix
        self._right_index: Optional[Dict[str, Dict[str, Any]]] = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_index(self) -> Dict[str, Dict[str, Any]]:
        index: Dict[str, Dict[str, Any]] = {}
        for row in self._right:
            key = row.get(self._on)
            if key is not None:
                index[str(key)] = row
        return index

    def _merge(self, left_row: Dict[str, Any], right_row: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        merged = dict(left_row)
        if right_row is not None:
            for k, v in right_row.items():
                if k == self._on:
                    continue
                dest = k if k not in merged else f"{self._right_prefix}{k}"
                merged[dest] = v
        return merged

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def join(self) -> Iterator[Dict[str, Any]]:
        """Yield merged rows according to the configured join strategy."""
        if self._right_index is None:
            self._right_index = self._build_index()

        for left_row in self._left:
            key = str(left_row.get(self._on, ""))
            right_row = self._right_index.get(key)
            if right_row is None and self._how == "inner":
                continue
            yield self._merge(left_row, right_row)

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        return self.join()
