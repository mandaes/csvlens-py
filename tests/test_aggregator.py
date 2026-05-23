"""Tests for CSVAggregator."""

import io
import pytest
from csvlens.reader import CSVReader
from csvlens.aggregator import CSVAggregator

CSV_DATA = """name,department,salary
Alice,Engineering,90000
Bob,Engineering,85000
Carol,Marketing,70000
Dave,Marketing,72000
Eve,Engineering,95000
"""


def _rows():
    reader = CSVReader(io.StringIO(CSV_DATA))
    return list(reader)


class TestCSVAggregatorCount:
    def test_count(self):
        agg = CSVAggregator(iter(_rows()))
        assert agg.count() == 5

    def test_count_by(self):
        agg = CSVAggregator(iter(_rows()))
        result = agg.count_by("department")
        assert result["Engineering"] == 3
        assert result["Marketing"] == 2


class TestCSVAggregatorNumeric:
    def test_sum(self):
        agg = CSVAggregator(iter(_rows()))
        assert agg.sum("salary") == 412000.0

    def test_avg(self):
        agg = CSVAggregator(iter(_rows()))
        assert agg.avg("salary") == pytest.approx(82400.0)

    def test_min(self):
        agg = CSVAggregator(iter(_rows()))
        assert agg.min("salary") == 70000.0

    def test_max(self):
        agg = CSVAggregator(iter(_rows()))
        assert agg.max("salary") == 95000.0

    def test_avg_empty(self):
        agg = CSVAggregator(iter([]))
        assert agg.avg("salary") is None

    def test_min_empty(self):
        agg = CSVAggregator(iter([]))
        assert agg.min("salary") is None

    def test_max_empty(self):
        agg = CSVAggregator(iter([]))
        assert agg.max("salary") is None


class TestCSVAggregatorUnique:
    def test_unique_values(self):
        agg = CSVAggregator(iter(_rows()))
        result = agg.unique("department")
        assert result == ["Engineering", "Marketing"]

    def test_unique_all_different(self):
        agg = CSVAggregator(iter(_rows()))
        result = agg.unique("name")
        assert len(result) == 5

    def test_sum_invalid_values_skipped(self):
        rows = [{"salary": "abc"}, {"salary": "50000"}, {"salary": ""}]
        agg = CSVAggregator(iter(rows))
        assert agg.sum("salary") == 50000.0
