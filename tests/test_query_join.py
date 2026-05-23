"""Integration tests: CSVQuery.join() fluent API."""
import pytest
from csvlens.query import CSVQuery


LEFT = [
    {"id": "1", "name": "Alice", "score": "90"},
    {"id": "2", "name": "Bob", "score": "75"},
    {"id": "3", "name": "Charlie", "score": "85"},
]

RIGHT = [
    {"id": "1", "dept": "Engineering"},
    {"id": "2", "dept": "Marketing"},
]


def _query():
    return CSVQuery(iter(LEFT))


class TestQueryJoinInner:
    def test_join_returns_query(self):
        result = _query().join(iter(RIGHT), on="id")
        assert isinstance(result, CSVQuery)

    def test_inner_join_row_count(self):
        rows = list(_query().join(iter(RIGHT), on="id", how="inner"))
        assert len(rows) == 2

    def test_inner_join_merged_fields(self):
        rows = list(_query().join(iter(RIGHT), on="id", how="inner"))
        alice = next(r for r in rows if r["name"] == "Alice")
        assert alice["dept"] == "Engineering"

    def test_inner_join_excludes_unmatched(self):
        rows = list(_query().join(iter(RIGHT), on="id", how="inner"))
        names = [r["name"] for r in rows]
        assert "Charlie" not in names


class TestQueryJoinLeft:
    def test_left_join_row_count(self):
        rows = list(_query().join(iter(RIGHT), on="id", how="left"))
        assert len(rows) == 3

    def test_left_join_unmatched_row_intact(self):
        rows = list(_query().join(iter(RIGHT), on="id", how="left"))
        charlie = next(r for r in rows if r["name"] == "Charlie")
        assert charlie == {"id": "3", "name": "Charlie", "score": "85"}


class TestQueryJoinWithFilter:
    def test_filter_before_join(self):
        """Filter left side first, then join."""
        rows = list(
            _query()
            .equals("name", "Alice")
            .join(iter(RIGHT), on="id", how="inner")
        )
        assert len(rows) == 1
        assert rows[0]["dept"] == "Engineering"

    def test_filter_after_join(self):
        """Join first, then filter the resulting query."""
        joined = _query().join(iter(RIGHT), on="id", how="left")
        rows = list(joined.equals("dept", "Marketing"))
        assert len(rows) == 1
        assert rows[0]["name"] == "Bob"

    def test_join_then_aggregate_count(self):
        joined = _query().join(iter(RIGHT), on="id", how="inner")
        assert joined.aggregate().count() == 2
