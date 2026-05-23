"""Integration tests: CSVQuery.sample() integration with CSVSampler."""

from __future__ import annotations

import io

import pytest

from csvlens.reader import CSVReader
from csvlens.query import CSVQuery


def _query(n_rows: int = 30) -> CSVQuery:
    lines = ["id,city,score"]
    for i in range(1, n_rows + 1):
        lines.append(f"{i},City{i},{i * 3}")
    buf = io.StringIO("\n".join(lines))
    reader = CSVReader(buf)
    return CSVQuery(reader)


class TestQuerySampleIntegration:
    def test_sample_first_returns_list(self):
        result = _query(20).sample().first(5)
        assert isinstance(result, list)
        assert len(result) == 5

    def test_sample_first_rows_are_dicts(self):
        result = _query(20).sample().first(3)
        assert all(isinstance(r, dict) for r in result)

    def test_sample_first_after_filter(self):
        # Filter keeps rows with score > 30 (i.e. id > 10), then take first 3
        result = (
            _query(30)
            .where("score")
            .greater_than("30")
            .sample()
            .first(3)
        )
        assert len(result) == 3
        assert all(int(r["score"]) > 30 for r in result)

    def test_sample_reservoir_count(self):
        result = _query(30).sample(seed=42).reservoir(10)
        assert len(result) == 10

    def test_sample_reservoir_reproducible(self):
        a = _query(30).sample(seed=7).reservoir(8)
        b = _query(30).sample(seed=7).reservoir(8)
        assert a == b

    def test_sample_every_nth_on_filtered(self):
        result = list(
            _query(20)
            .where("id")
            .greater_than("0")
            .sample()
            .every_nth(2)
        )
        # 20 rows pass the filter; every_nth(2) should yield 10
        assert len(result) == 10
