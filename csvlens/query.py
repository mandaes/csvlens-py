from typing import Iterator, Dict, Any, Optional
from csvlens.reader import CSVReader
from csvlens.filter import RowFilter
from csvlens.aggregator import CSVAggregator
from csvlens.sorter import CSVSorter
from csvlens.paginator import CSVPaginator


class CSVQuery:
    """Fluent interface for filtering, sorting, aggregating, and paginating CSV data."""

    def __init__(self, reader: CSVReader):
        self._reader = reader
        self._filter = RowFilter()
        self._sort_key: Optional[str] = None
        self._sort_asc: bool = True

    def where(self, column: str) -> "CSVQuery":
        self._active_column = column
        return self

    def equals(self, value: str) -> "CSVQuery":
        self._filter.equals(self._active_column, value)
        return self

    def contains(self, value: str) -> "CSVQuery":
        self._filter.contains(self._active_column, value)
        return self

    def greater_than(self, value: float) -> "CSVQuery":
        self._filter.greater_than(self._active_column, value)
        return self

    def less_than(self, value: float) -> "CSVQuery":
        self._filter.less_than(self._active_column, value)
        return self

    def order_by(self, column: str, ascending: bool = True) -> "CSVQuery":
        self._sort_key = column
        self._sort_asc = ascending
        return self

    def _iter_filtered(self) -> Iterator[Dict[str, Any]]:
        for row in self._reader:
            if self._filter.apply(row):
                yield row

    def fetch(self):
        rows = self._iter_filtered()
        if self._sort_key:
            sorter = CSVSorter(rows)
            if self._sort_asc:
                return sorter.asc(self._sort_key)
            else:
                return sorter.desc(self._sort_key)
        return list(rows)

    def aggregate(self) -> "CSVAggregator":
        return CSVAggregator(self._iter_filtered())

    def paginate(self, page_size: int = 100) -> "CSVPaginator":
        """Return a CSVPaginator over the filtered (and optionally sorted) rows."""
        rows = self._iter_filtered()
        if self._sort_key:
            sorter = CSVSorter(rows)
            if self._sort_asc:
                sorted_rows = iter(sorter.asc(self._sort_key))
            else:
                sorted_rows = iter(sorter.desc(self._sort_key))
            return CSVPaginator(sorted_rows, page_size=page_size)
        return CSVPaginator(rows, page_size=page_size)
