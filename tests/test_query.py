"""Tests for the fluent CSVQuery interface."""

import io
import pytest
from csvlens.reader import CSVReader
from csvlens.query import CSVQuery


CSV_DATA = """name,age,city
Alice,30,New York
Bob,25,London
Carol,35,New York
Dave,28,Berlin
Eve,30,London
"""


def _query():
    reader = CSVReader(io.StringIO(CSV_DATA))
    return CSVQuery(reader)


class TestCSVQueryFiltering:
    def test_equals_filter(self):
        results = _query().equals("city", "New York").to_list()
        assert len(results) == 2
        assert all(r["city"] == "New York" for r in results)

    def test_contains_filter(self):
        results = _query().contains("name", "e").to_list()
        names = [r["name"] for r in results]
        assert "Eve" in names
        assert "Dave" in names

    def test_greater_than_filter(self):
        results = _query().greater_than("age", 29).to_list()
        assert all(float(r["age"]) > 29 for r in results)

    def test_chained_filters(self):
        results = (
            _query()
            .equals("city", "London")
            .greater_than("age", 26)
            .to_list()
        )
        assert len(results) == 1
        assert results[0]["name"] == "Eve"

    def test_custom_where(self):
        results = _query().where(lambda r: r["name"].startswith("C")).to_list()
        assert len(results) == 1
        assert results[0]["name"] == "Carol"


class TestCSVQueryProjection:
    def test_select_columns(self):
        results = _query().select("name", "city").to_list()
        assert all(set(r.keys()) == {"name", "city"} for r in results)

    def test_select_missing_column_ignored(self):
        results = _query().select("name", "nonexistent").to_list()
        assert all("nonexistent" not in r for r in results)


class TestCSVQueryLimit:
    def test_limit(self):
        results = _query().limit(2).to_list()
        assert len(results) == 2

    def test_limit_with_filter(self):
        results = _query().greater_than("age", 24).limit(3).to_list()
        assert len(results) == 3


class TestCSVQueryCount:
    def test_count(self):
        assert _query().equals("city", "London").count() == 2

    def test_count_all(self):
        assert _query().count() == 5


class TestCSVQueryIterable:
    def test_iterable(self):
        rows = list(_query().equals("city", "Berlin"))
        assert len(rows) == 1
        assert rows[0]["name"] == "Dave"
