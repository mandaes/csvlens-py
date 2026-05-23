from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional


class CSVCaster:
    """
    Lazily casts column values to specified Python types as rows are iterated.
    Supports built-in types (int, float, bool) and custom cast functions.
    Uncastable values can either raise or fall back to a default.
    """

    def __init__(self, rows: Iterable[Dict[str, str]]) -> None:
        self._rows = rows
        self._casts: Dict[str, Callable[[str], Any]] = {}
        self._defaults: Dict[str, Any] = {}

    def as_int(self, column: str, default: Optional[int] = None) -> "CSVCaster":
        """Cast column values to int."""
        self._casts[column] = int
        if default is not None:
            self._defaults[column] = default
        return self

    def as_float(self, column: str, default: Optional[float] = None) -> "CSVCaster":
        """Cast column values to float."""
        self._casts[column] = float
        if default is not None:
            self._defaults[column] = default
        return self

    def as_bool(self, column: str, default: Optional[bool] = None) -> "CSVCaster":
        """Cast column values to bool. Truthy strings: '1', 'true', 'yes'."""
        def _bool(val: str) -> bool:
            return val.strip().lower() in ("1", "true", "yes")
        self._casts[column] = _bool
        if default is not None:
            self._defaults[column] = default
        return self

    def as_type(self, column: str, fn: Callable[[str], Any], default: Any = None) -> "CSVCaster":
        """Cast column values using a custom callable."""
        self._casts[column] = fn
        if default is not None:
            self._defaults[column] = default
        return self

    def _cast_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        result: Dict[str, Any] = dict(row)
        for col, fn in self._casts.items():
            if col not in result:
                continue
            raw = result[col]
            try:
                result[col] = fn(raw)
            except (ValueError, TypeError):
                if col in self._defaults:
                    result[col] = self._defaults[col]
                else:
                    raise ValueError(
                        f"Cannot cast column '{col}' value {raw!r} and no default provided."
                    )
        return result

    def rows(self) -> List[Dict[str, Any]]:
        """Return all cast rows as a list."""
        return list(self)

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        for row in self._rows:
            yield self._cast_row(row)
