"""Tests for CSVProfiler."""

import pytest
from csvlens.profiler import CSVProfiler


def _rows():
    return [
        {"name": "Alice", "age": "30", "score": "88.5"},
        {"name": "Bob",   "age": "25", "score": "72.0"},
        {"name": "Carol", "age": "30", "score": ""},
        {"name": "Dave",  "age": "",   "score": "95.0"},
        {"name": "Eve",   "age": "28", "score": "72.0"},
    ]


class TestCSVProfilerCounts:
    def test_count_non_empty(self):
        p = CSVProfiler(_rows())
        assert p.column("age")["count"] == 4

    def test_null_count(self):
        p = CSVProfiler(_rows())
        assert p.column("age")["null_count"] == 1

    def test_count_plus_null_equals_total(self):
        p = CSVProfiler(_rows())
        col = p.column("score")
        assert col["count"] + col["null_count"] == 5


class TestCSVProfilerUnique:
    def test_unique_values(self):
        p = CSVProfiler(_rows())
        assert p.column("age")["unique"] == {"25", "28", "30"}

    def test_unique_cap_limits_set_size(self):
        rows = [{"x": str(i)} for i in range(200)]
        p = CSVProfiler(rows, unique_cap=50)
        assert len(p.column("x")["unique"]) <= 50


class TestCSVProfilerMinMax:
    def test_min_lexicographic(self):
        p = CSVProfiler(_rows())
        assert p.column("name")["min"] == "Alice"

    def test_max_lexicographic(self):
        p = CSVProfiler(_rows())
        assert p.column("name")["max"] == "Eve"


class TestCSVProfilerNumeric:
    def test_numeric_flag_true_for_age(self):
        p = CSVProfiler(_rows())
        # age has one empty value → numeric_flag becomes False
        assert p.column("age")["numeric"] is False

    def test_numeric_flag_true_for_all_numeric(self):
        rows = [{"v": "1.0"}, {"v": "2.5"}, {"v": "3"}]
        p = CSVProfiler(rows)
        assert p.column("v")["numeric"] is True

    def test_numeric_flag_false_for_name(self):
        p = CSVProfiler(_rows())
        assert p.column("name")["numeric"] is False

    def test_sum(self):
        rows = [{"v": "10"}, {"v": "20"}, {"v": "30"}]
        p = CSVProfiler(rows)
        assert p.column("v")["sum"] == pytest.approx(60.0)

    def test_mean(self):
        rows = [{"v": "10"}, {"v": "20"}, {"v": "30"}]
        p = CSVProfiler(rows)
        assert p.column("v")["mean"] == pytest.approx(20.0)

    def test_min_num_and_max_num(self):
        rows = [{"v": "5"}, {"v": "1"}, {"v": "9"}]
        p = CSVProfiler(rows)
        col = p.column("v")
        assert col["min_num"] == pytest.approx(1.0)
        assert col["max_num"] == pytest.approx(9.0)

    def test_no_numeric_keys_when_not_numeric(self):
        p = CSVProfiler(_rows())
        col = p.column("name")
        assert "sum" not in col
        assert "mean" not in col


class TestCSVProfilerFullProfile:
    def test_profile_returns_all_columns(self):
        p = CSVProfiler(_rows())
        assert set(p.profile().keys()) == {"name", "age", "score"}

    def test_column_key_error_on_missing(self):
        p = CSVProfiler(_rows())
        with pytest.raises(KeyError):
            p.column("nonexistent")
