"""Tests for CSVSampler."""

from __future__ import annotations

import pytest

from csvlens.sampler import CSVSampler


def _rows(n: int = 20) -> list[dict]:
    return [{"id": str(i), "value": str(i * 10)} for i in range(1, n + 1)]


# ---------------------------------------------------------------------------
# first()
# ---------------------------------------------------------------------------

class TestCSVSamplerFirst:
    def test_first_returns_correct_count(self):
        result = CSVSampler(_rows(20)).first(5)
        assert len(result) == 5

    def test_first_returns_leading_rows(self):
        result = CSVSampler(_rows(20)).first(3)
        assert [r["id"] for r in result] == ["1", "2", "3"]

    def test_first_zero(self):
        assert CSVSampler(_rows(20)).first(0) == []

    def test_first_more_than_available(self):
        result = CSVSampler(_rows(5)).first(100)
        assert len(result) == 5

    def test_first_negative_raises(self):
        with pytest.raises(ValueError):
            CSVSampler(_rows()).first(-1)


# ---------------------------------------------------------------------------
# reservoir()
# ---------------------------------------------------------------------------

class TestCSVSamplerReservoir:
    def test_reservoir_exact_count(self):
        result = CSVSampler(_rows(20), seed=42).reservoir(7)
        assert len(result) == 7

    def test_reservoir_all_rows_are_dicts(self):
        result = CSVSampler(_rows(20), seed=0).reservoir(5)
        assert all(isinstance(r, dict) for r in result)

    def test_reservoir_fewer_rows_than_n(self):
        result = CSVSampler(_rows(3), seed=1).reservoir(10)
        assert len(result) == 3

    def test_reservoir_zero(self):
        assert CSVSampler(_rows(20), seed=1).reservoir(0) == []

    def test_reservoir_reproducible_with_seed(self):
        a = CSVSampler(_rows(50), seed=99).reservoir(10)
        b = CSVSampler(_rows(50), seed=99).reservoir(10)
        assert a == b

    def test_reservoir_negative_raises(self):
        with pytest.raises(ValueError):
            CSVSampler(_rows()).reservoir(-1)


# ---------------------------------------------------------------------------
# every_nth()
# ---------------------------------------------------------------------------

class TestCSVSamplerEveryNth:
    def test_every_1_returns_all(self):
        result = list(CSVSampler(_rows(10)).every_nth(1))
        assert len(result) == 10

    def test_every_2_returns_half(self):
        result = list(CSVSampler(_rows(10)).every_nth(2))
        assert len(result) == 5
        assert result[0]["id"] == "1"
        assert result[1]["id"] == "3"

    def test_every_nth_zero_raises(self):
        with pytest.raises(ValueError):
            list(CSVSampler(_rows()).every_nth(0))


# ---------------------------------------------------------------------------
# fraction()
# ---------------------------------------------------------------------------

class TestCSVSamplerFraction:
    def test_fraction_zero_returns_empty(self):
        result = CSVSampler(_rows(100), seed=7).fraction(0.0)
        assert result == []

    def test_fraction_one_returns_all(self):
        result = CSVSampler(_rows(20), seed=7).fraction(1.0)
        assert len(result) == 20

    def test_fraction_out_of_range_raises(self):
        with pytest.raises(ValueError):
            CSVSampler(_rows()).fraction(1.5)

    def test_fraction_returns_list_of_dicts(self):
        result = CSVSampler(_rows(50), seed=3).fraction(0.5)
        assert all(isinstance(r, dict) for r in result)
