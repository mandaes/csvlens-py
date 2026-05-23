import io
import pytest
from csvlens.query import CSVQuery
from csvlens.reader import CSVReader


# ---------------------------------------------------------------------------
# fixture
# ---------------------------------------------------------------------------

CSV_DATA = """name,dept,salary
Alice,Engineering,90000
Bob,Marketing,70000
Alice,Engineering,90000
Carol,Engineering,85000
Bob,Marketing,70000
Dave,Marketing,72000
"""


def _query():
    reader = CSVReader(io.StringIO(CSV_DATA))
    return CSVQuery(reader)


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------

class TestQueryDedupIntegration:

    def test_dedup_returns_deduplicator(self):
        from csvlens.deduplicator import CSVDeduplicator
        d = _query().dedup()
        assert isinstance(d, CSVDeduplicator)

    def test_dedup_full_row_count(self):
        result = _query().dedup().unique()
        assert len(result) == 4

    def test_dedup_by_key_count(self):
        result = _query().dedup(keys=["name"]).unique()
        names = [r["name"] for r in result]
        assert sorted(names) == ["Alice", "Bob", "Carol", "Dave"]

    def test_dedup_after_filter(self):
        result = (
            _query()
            .where("dept").equals("Marketing")
            .dedup(keys=["name"])
            .unique()
        )
        names = [r["name"] for r in result]
        assert sorted(names) == ["Bob", "Dave"]

    def test_dedup_rows_are_dicts(self):
        result = _query().dedup().unique()
        assert all(isinstance(r, dict) for r in result)
