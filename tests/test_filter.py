"""Tests for RowFilter lazy filtering."""

import io
import pytest
from csvlens.reader import CSVReader
from csvlens.filter import RowFilter


CSV_DATA = """name,age,city
Alice,30,New York
Bob,25,London
Carol,35,New York
Dave,28,Berlin
Eve,30,London
"""


def _make_reader():
    return CSVReader(io.StringIO(CSV_DATA))


def _rows(reader):
    return list(reader)


class TestRowFilterEquals:
    def test_equals_match(self):
        f = RowFilter.equals("city", "London")
        results = list(f.apply(iter(_rows(_make_reader()))))
        assert len(results) == 2
        assert all(r["city"] == "London" for r in results)

    def test_equals_no_match(self):
        f = RowFilter.equals("city", "Tokyo")
        results = list(f.apply(iter(_rows(_make_reader()))))
        assert results == []


class TestRowFilterContains:
    def test_contains_match(self):
        f = RowFilter.contains("name", "a")
        results = list(f.apply(iter(_rows(_make_reader()))))
        names = [r["name"] for r in results]
        assert "Carol" in names
        assert "Dave" in names

    def test_contains_case_sensitive(self):
        f = RowFilter.contains("name", "A")
        results = list(f.apply(iter(_rows(_make_reader()))))
        assert all("A" in r["name"] for r in results)


class TestRowFilterNumeric:
    def test_greater_than(self):
        f = RowFilter.greater_than("age", 29)
        results = list(f.apply(iter(_rows(_make_reader()))))
        assert all(float(r["age"]) > 29 for r in results)
        assert len(results) == 3  # Alice(30), Carol(35), Eve(30)

    def test_less_than(self):
        f = RowFilter.less_than("age", 29)
        results = list(f.apply(iter(_rows(_make_reader()))))
        assert all(float(r["age"]) < 29 for r in results)
        assert len(results) == 2  # Bob(25), Dave(28)

    def test_non_numeric_skipped(self):
        f = RowFilter.greater_than("name", 10)
        results = list(f.apply(iter(_rows(_make_reader()))))
        assert results == []


class TestRowFilterCombine:
    def test_combine_and(self):
        f = RowFilter.combine(
            RowFilter.equals("city", "London"),
            RowFilter.greater_than("age", 26),
        )
        results = list(f.apply(iter(_rows(_make_reader()))))
        assert len(results) == 1
        assert results[0]["name"] == "Eve"
