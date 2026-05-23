from typing import Iterator, List, Dict, Any, Optional


class CSVSorter:
    """
    Lazily sorts rows from a CSV stream by one or more columns.
    Sorting requires materializing the relevant portion of the stream,
    but does so only once and yields results lazily afterward.
    """

    def __init__(self, rows: Iterator[Dict[str, Any]]):
        self._rows = rows
        self._sort_keys: List[Dict[str, Any]] = []

    def order_by(self, column: str, descending: bool = False) -> "CSVSorter":
        """Add a sort key. Multiple calls create a multi-key sort."""
        self._sort_keys.append({"column": column, "descending": descending})
        return self

    def asc(self, column: str) -> "CSVSorter":
        """Sort by column ascending."""
        return self.order_by(column, descending=False)

    def desc(self, column: str) -> "CSVSorter":
        """Sort by column descending."""
        return self.order_by(column, descending=True)

    def _coerce(self, value: str) -> Any:
        """Try to coerce a string value to a numeric type for comparison."""
        try:
            return float(value)
        except (ValueError, TypeError):
            return value

    def _sort_key(self, row: Dict[str, Any]):
        return tuple(
            self._coerce(row.get(k["column"], ""))
            for k in self._sort_keys
        )

    def sorted_rows(self) -> Iterator[Dict[str, Any]]:
        """Materialize and sort all rows, then yield them one by one."""
        if not self._sort_keys:
            yield from self._rows
            return

        # Determine per-key descending flags for multi-key sort
        # Python's sort is stable, so we do a single pass with tuple key
        # and handle descending by negating numeric values or reversing strings
        materialized = list(self._rows)

        # For simplicity with mixed types, sort once using tuple key
        # For descending, we reverse the whole sort if only one key;
        # for multi-key we rely on a combined approach.
        if len(self._sort_keys) == 1:
            key_info = self._sort_keys[0]
            col = key_info["column"]
            reverse = key_info["descending"]
            materialized.sort(
                key=lambda r: self._coerce(r.get(col, "")),
                reverse=reverse
            )
        else:
            # Multi-key: sort from least significant to most significant
            for key_info in reversed(self._sort_keys):
                col = key_info["column"]
                reverse = key_info["descending"]
                materialized.sort(
                    key=lambda r, c=col: self._coerce(r.get(c, "")),
                    reverse=reverse
                )

        yield from materialized

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        return self.sorted_rows()
