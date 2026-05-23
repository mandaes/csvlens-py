"""Tests for CSVQuery.aggregate() integration."""

import io
import pytest
from csvlens.reader import CSVReader
from csvlens.query import CSVQuery

CSV_DATA = """name,department,salary
Alice,Engineering,90000
Bob,Engineering,85000
Carol,Marketing,70000
Dave,Marketing,72000
Eve,Engineering,95000
"""


def _query():
    reader = CSVReader(io.StringIO(CSV_DATA))
    return CSVQuery(reader)


class TestQueryAggregate:
    def test_aggregate_count_all(self):
        result = _query().aggregate().count()
        assert result == 5

    def test_aggregate_count_filtered(self):
        result = _query().equals("department", "Engineering").aggregate().count()
        assert result == 3

    def test_aggregate_sum_filtered(self):
        result = (
            _query()
            .equals("department", "Engineering")
            .aggregate()
            .sum("salary")
        )
        assert result == 270000.0

    def test_aggregate_avg_filtered(self):
        result = (
            _query()
            .equals("department", "Marketing")
            .aggregate()
            .avg("salary")
        )
        assert result == pytest.approx(71000.0)

    def test_aggregate_max_with_greater_than(self):
        result = (
            _query()
            .greater_than("salary", 80000)
            .aggregate()
            .max("salary")
        )
        assert result == 95000.0

    def test_aggregate_min(self):
        """Test that min() returns the smallest value across all rows."""
        result = _query().aggregate().min("salary")
        assert result == 70000.0

    def test_aggregate_min_filtered(self):
        """Test that min() respects an active filter."""
        result = (
            _query()
            .equals("department", "Engineering")
            .aggregate()
            .min("salary")
        )
        assert result == 85000.0

    def test_aggregate_count_by_after_filter(self):
        result = (
            _query()
            .greater_than("salary", 71000)
            .aggregate()
            .count_by("department")
        )
        assert result.get("Engineering") == 3
        assert result.get("Marketing") == 1

    def test_aggregate_unique_departments(self):
        result = _query().aggregate().unique("department")
        assert result == ["Engineering", "Marketing"]
