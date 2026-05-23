"""Row transformation utilities for csvlens."""
from typing import Callable, Dict, Iterable, Iterator, List, Optional


class CSVTransformer:
    """Applies field-level transformations to rows lazily."""

    def __init__(self, rows: Iterable[Dict[str, str]]) -> None:
        self._rows = rows
        self._transforms: List[tuple] = []  # (field, callable)

    def apply(self, field: str, func: Callable[[str], str]) -> "CSVTransformer":
        """Register a transformation function for a specific field."""
        self._transforms.append((field, func))
        return self

    def rename(self, old_name: str, new_name: str) -> "CSVTransformer":
        """Rename a field in every row."""
        def _rename(row: Dict[str, str]) -> Dict[str, str]:
            if old_name in row:
                row[new_name] = row.pop(old_name)
            return row
        self._transforms.append((None, _rename))
        return self

    def add_field(
        self,
        field: str,
        func: Callable[[Dict[str, str]], str],
    ) -> "CSVTransformer":
        """Add a computed field derived from the whole row."""
        def _add(row: Dict[str, str]) -> Dict[str, str]:
            row[field] = func(row)
            return row
        self._transforms.append((None, _add))
        return self

    def drop_field(self, field: str) -> "CSVTransformer":
        """Remove a field from every row."""
        def _drop(row: Dict[str, str]) -> Dict[str, str]:
            row.pop(field, None)
            return row
        self._transforms.append((None, _drop))
        return self

    def _apply_transforms(self, row: Dict[str, str]) -> Dict[str, str]:
        row = dict(row)  # work on a copy
        for field, func in self._transforms:
            if field is not None:
                if field in row:
                    row[field] = func(row[field])
            else:
                row = func(row)
        return row

    def __iter__(self) -> Iterator[Dict[str, str]]:
        for row in self._rows:
            yield self._apply_transforms(row)

    def to_list(self) -> List[Dict[str, str]]:
        """Materialise all transformed rows into a list."""
        return list(self)
