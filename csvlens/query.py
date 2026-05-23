from csvlens.reader import CSVReader
from csvlens.filter import RowFilter
from csvlens.aggregator import CSVAggregator
from csvlens.sorter import CSVSorter
from csvlens.paginator import CSVPaginator
from csvlens.exporter import CSVExporter
from typing import Optional, Iterator, Dict, Any


class CSVQuery:
    """
    Fluent query interface over a CSV file.
    Supports filtering, sorting, pagination, aggregation, and export.
    """

    def __init__(self, reader: CSVReader):
        self._reader = reader
        self._filters = []
        self._sort_key: Optional[str] = None
        self._sort_reverse: bool = False

    def where(self, column: str) -> "CSVQuery":
        self._pending_column = column
        return self

    def equals(self, value: str) -> "CSVQuery":
        self._filters.append(RowFilter(self._pending_column).equals(value))
        return self

    def contains(self, value: str) -> "CSVQuery":
        self._filters.append(RowFilter(self._pending_column).contains(value))
        return self

    def greater_than(self, value: float) -> "CSVQuery":
        self._filters.append(RowFilter(self._pending_column).greater_than(value))
        return self

    def less_than(self, value: float) -> "CSVQuery":
        self._filters.append(RowFilter(self._pending_column).less_than(value))
        return self

    def order_by(self, column: str, ascending: bool = True) -> "CSVQuery":
        self._sort_key = column
        self._sort_reverse = not ascending
        return self

    def _iter_filtered(self) -> Iterator[Dict[str, Any]]:
        for row in self._reader:
            if all(f.apply(row) for f in self._filters):
                yield row

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        rows = self._iter_filtered()
        if self._sort_key:
            sorter = CSVSorter(rows)
            if self._sort_reverse:
                rows = iter(sorter.desc(self._sort_key))
            else:
                rows = iter(sorter.asc(self._sort_key))
        return rows

    def paginate(self, page_size: int = 50) -> CSVPaginator:
        return CSVPaginator(self, page_size=page_size)

    def aggregate(self) -> CSVAggregator:
        return CSVAggregator(self)

    def export(self) -> CSVExporter:
        """Return a CSVExporter for the current query results."""
        return CSVExporter(self)
