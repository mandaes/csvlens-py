"""Tests for CSVJoiner."""
import pytest
from csvlens.joiner import CSVJoiner


LEFT_ROWS = [
    {"id": "1", "name": "Alice"},
    {"id": "2", "name": "Bob"},
    {"id": "3", "name": "Charlie"},
]

RIGHT_ROWS = [
    {"id": "1", "dept": "Engineering"},
    {"id": "2", "dept": "Marketing"},
    # id 3 intentionally missing
]


def _inner_join(**kwargs):
    return CSVJoiner(iter(LEFT_ROWS), iter(RIGHT_ROWS), on="id", how="inner", **kwargs)


def _left_join(**kwargs):
    return CSVJoiner(iter(LEFT_ROWS), iter(RIGHT_ROWS), on="id", how="left", **kwargs)


class TestCSVJoinerInner:
    def test_inner_row_count(self):
        rows = list(_inner_join().join())
        assert len(rows) == 2

    def test_inner_contains_merged_fields(self):
        rows = list(_inner_join().join())
        assert rows[0] == {"id": "1", "name": "Alice", "dept": "Engineering"}
        assert rows[1] == {"id": "2", "name": "Bob", "dept": "Marketing"}

    def test_inner_excludes_unmatched_left(self):
        ids = [r["id"] for r in _inner_join().join()]
        assert "3" not in ids

    def test_iter_protocol(self):
        rows = list(_inner_join())
        assert len(rows) == 2


class TestCSVJoinerLeft:
    def test_left_row_count(self):
        rows = list(_left_join().join())
        assert len(rows) == 3

    def test_left_unmatched_has_no_right_fields(self):
        rows = list(_left_join().join())
        charlie = next(r for r in rows if r["id"] == "3")
        assert charlie == {"id": "3", "name": "Charlie"}

    def test_left_matched_rows_correct(self):
        rows = list(_left_join().join())
        alice = next(r for r in rows if r["id"] == "1")
        assert alice["dept"] == "Engineering"


class TestCSVJoinerCollisions:
    def test_right_prefix_applied_on_collision(self):
        left = [{"id": "1", "name": "Alice", "dept": "OldDept"}]
        right = [{"id": "1", "dept": "Engineering"}]
        rows = list(CSVJoiner(iter(left), iter(right), on="id", right_prefix="r_").join())
        assert rows[0]["dept"] == "OldDept"
        assert rows[0]["r_dept"] == "Engineering"

    def test_join_key_not_duplicated(self):
        rows = list(_inner_join().join())
        # 'id' should appear exactly once
        assert list(rows[0].keys()).count("id") == 1


class TestCSVJoinerValidation:
    def test_invalid_how_raises(self):
        with pytest.raises(ValueError, match="Unsupported join type"):
            CSVJoiner(iter([]), iter([]), on="id", how="outer")

    def test_empty_left_returns_nothing(self):
        rows = list(CSVJoiner(iter([]), iter(RIGHT_ROWS), on="id").join())
        assert rows == []

    def test_empty_right_inner_returns_nothing(self):
        rows = list(CSVJoiner(iter(LEFT_ROWS), iter([]), on="id", how="inner").join())
        assert rows == []

    def test_empty_right_left_join_returns_all_left(self):
        rows = list(CSVJoiner(iter(LEFT_ROWS), iter([]), on="id", how="left").join())
        assert len(rows) == 3
