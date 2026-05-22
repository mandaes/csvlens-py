"""Core streaming CSV reader for csvlens-py.

Provides lazy, memory-efficient iteration over large CSV files
without loading the entire file into memory.
"""

from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Generator, Iterator, Optional, Union


class CSVReader:
    """Lazily streams rows from a CSV file one at a time.

    Parameters
    ----------
    source:
        A file path (str or Path) or a file-like object opened in text mode.
    delimiter:
        Field delimiter character. Defaults to ','.
    has_header:
        Whether the first row should be treated as a header. Defaults to True.
    encoding:
        File encoding when *source* is a path. Defaults to 'utf-8'.
    """

    def __init__(
        self,
        source: Union[str, Path, io.TextIOBase],
        delimiter: str = ",",
        has_header: bool = True,
        encoding: str = "utf-8",
    ) -> None:
        self._source = source
        self._delimiter = delimiter
        self._has_header = has_header
        self._encoding = encoding
        self._headers: Optional[list[str]] = None
        self._file_handle: Optional[io.TextIOWrapper] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def headers(self) -> Optional[list[str]]:
        """Return the header row, or *None* if *has_header* is False."""
        return self._headers

    def rows(self) -> Generator[dict[str, str] | list[str], None, None]:
        """Yield rows lazily from the CSV source.

        Yields
        ------
        dict[str, str]
            When *has_header* is True, each row is a mapping of column
            name → value.
        list[str]
            When *has_header* is False, each row is a plain list of values.
        """
        for row in self._iter_rows():
            yield row

    def __iter__(self) -> Iterator[dict[str, str] | list[str]]:
        return self.rows()

    def __enter__(self) -> "CSVReader":
        return self

    def __exit__(self, *_: object) -> None:
        self._close()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _open(self) -> io.TextIOBase:
        if isinstance(self._source, (str, Path)):
            handle = open(self._source, newline="", encoding=self._encoding)
            self._file_handle = handle  # type: ignore[assignment]
            return handle
        return self._source  # already a file-like object

    def _close(self) -> None:
        if self._file_handle is not None:
            self._file_handle.close()
            self._file_handle = None

    def _iter_rows(
        self,
    ) -> Generator[dict[str, str] | list[str], None, None]:
        fh = self._open()
        try:
            reader = csv.reader(fh, delimiter=self._delimiter)
            if self._has_header:
                self._headers = next(reader, [])
                for raw in reader:
                    yield dict(zip(self._headers, raw))
            else:
                for raw in reader:
                    yield raw
        finally:
            self._close()
