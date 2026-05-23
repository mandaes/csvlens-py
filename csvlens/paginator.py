from typing import Iterator, List, Dict, Any, Optional


class CSVPaginator:
    """
    Provides page-based access to rows from a CSV source without
    loading the entire dataset into memory.
    """

    def __init__(self, rows: Iterator[Dict[str, Any]], page_size: int = 100):
        if page_size < 1:
            raise ValueError("page_size must be at least 1")
        self._rows = rows
        self._page_size = page_size
        self._buffer: List[Dict[str, Any]] = []
        self._exhausted = False
        self._total_loaded = 0

    @property
    def page_size(self) -> int:
        return self._page_size

    def _load_until(self, target: int) -> None:
        """Load rows from the iterator until we have `target` rows buffered."""
        if self._exhausted:
            return
        while len(self._buffer) < target:
            try:
                row = next(self._rows)
                self._buffer.append(row)
                self._total_loaded += 1
            except StopIteration:
                self._exhausted = True
                break

    def get_page(self, page_number: int) -> List[Dict[str, Any]]:
        """Return rows for a 1-indexed page number."""
        if page_number < 1:
            raise ValueError("page_number must be at least 1")
        start = (page_number - 1) * self._page_size
        end = start + self._page_size
        self._load_until(end)
        return self._buffer[start:end]

    def has_page(self, page_number: int) -> bool:
        """Return True if the given page has at least one row."""
        if page_number < 1:
            return False
        start = (page_number - 1) * self._page_size
        self._load_until(start + 1)
        return start < len(self._buffer)

    def total_loaded(self) -> int:
        """Return the number of rows loaded so far."""
        return self._total_loaded

    def pages(self) -> Iterator[List[Dict[str, Any]]]:
        """Iterate over all pages lazily."""
        page_number = 1
        while True:
            page = self.get_page(page_number)
            if not page:
                break
            yield page
            page_number += 1
