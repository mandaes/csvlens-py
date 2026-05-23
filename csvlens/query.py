"""CSVQuery: fluent query interface over a CSVReader."""
from typing import Any, Callable, Dict, Iterable, Iterator, Optional

from csvlens.filter import RowFilter
from csvlens.sorter import CSVSorter
from csvlens.paginator import CSVPaginator
from csvlens.exporter import CSVExporter
from csvlens.transformer import CSVTransformer
from csvlens.aggregator import CSVAggregator
from csvlens.joiner import CSVJoiner


class CSVQuery:
    """Fluent, lazy query builder for CSV row iterables."""

    def __init__(self, reader: Iterable[Dict[str, Any]]) -> None:
        self._reader = reader
        self._filters: list = []
        self._sorter: Optional[CSVSorter] = None
        self._transformer: Optional[CSVTransformer] = None

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def where(self, field: str) -> "RowFilter":
        f = RowFilter(field, self)
        self._filters.append(f)
        return f

    def equals(self, field: str, value: Any) -> "CSVQuery":
        return self.where(field).equals(value)

    def contains(self, field: str, value: str) -> "CSVQuery":
        return self.where(field).contains(value)

    def greater_than(self, field: str, value: float) -> "CSVQuery":
        return self.where(field).greater_than(value)

    def less_than(self, field: str, value: float) -> "CSVQuery":
        return self.where(field).less_than(value)

    # ------------------------------------------------------------------
    # Sorting
    # ------------------------------------------------------------------

    def order_by(self, field: str, direction: str = "asc") -> "CSVQuery":
        self._sorter = CSVSorter(self._iter_filtered(), field, direction)
        return self

    # ------------------------------------------------------------------
    # Transformation
    # ------------------------------------------------------------------

    def transform(self, field: str, fn: Callable[[Any], Any]) -> "CSVQuery":
        if self._transformer is None:
            self._transformer = CSVTransformer([])
        self._transformer.apply(field, fn)
        return self

    def rename(self, old: str, new: str) -> "CSVQuery":
        if self._transformer is None:
            self._transformer = CSVTransformer([])
        self._transformer.rename(old, new)
        return self

    # ------------------------------------------------------------------
    # Joining
    # ------------------------------------------------------------------

    def join(
        self,
        right: Iterable[Dict[str, Any]],
        on: str,
        how: str = "inner",
        right_prefix: str = "right_",
    ) -> "CSVQuery":
        """Return a new CSVQuery whose source is the result of a join."""
        joiner = CSVJoiner(
            self._iter_all(),
            right,
            on=on,
            how=how,
            right_prefix=right_prefix,
        )
        new_query = CSVQuery(joiner)
        return new_query

    # ------------------------------------------------------------------
    # Terminal / aggregation
    # ------------------------------------------------------------------

    def aggregate(self) -> CSVAggregator:
        return CSVAggregator(self._iter_all())

    def paginate(self, page_size: int = 50) -> CSVPaginator:
        return CSVPaginator(self._iter_all(), page_size=page_size)

    def export(self) -> CSVExporter:
        return CSVExporter(self._iter_all())

    # ------------------------------------------------------------------
    # Iteration helpers
    # ------------------------------------------------------------------

    def _iter_filtered(self) -> Iterator[Dict[str, Any]]:
        for row in self._reader:
            if all(f.match(row) for f in self._filters):
                yield row

    def _iter_all(self) -> Iterator[Dict[str, Any]]:
        base = self._sorter if self._sorter else self._iter_filtered()
        if self._transformer:
            yield from self._transformer.transform(base)
        else:
            yield from base

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        return self._iter_all()
