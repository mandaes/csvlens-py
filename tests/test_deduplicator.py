import pytest
from csvlens.deduplicator import CSVDeduplicator


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _rows_with_dupes():
    return [
        {"city": "London",   "country": "UK"},
        {"city": "Paris",    "country": "FR"},
        {"city": "London",   "country": "UK"},   # full duplicate
        {"city": "Berlin",   "country": "DE"},
        {"city": "Paris",    "country": "FR"},   # full duplicate
        {"city": "London",   "country": "DE"},   # same city, different country
    ]


def _dedup(keys=None):
    return CSVDeduplicator(iter(_rows_with_dupes()), keys=keys)


# ---------------------------------------------------------------------------
# full-row deduplication
# ---------------------------------------------------------------------------

class TestCSVDeduplicatorFullRow:

    def test_unique_count(self):
        assert _dedup().count() == 4

    def test_unique_returns_list_of_dicts(self):
        result = _dedup().unique()
        assert all(isinstance(r, dict) for r in result)

    def test_unique_first_occurrence_kept(self):
        result = _dedup().unique()
        cities = [r["city"] for r in result]
        assert cities.index("London") < cities.index("Berlin")

    def test_duplicates_count(self):
        assert len(_dedup().duplicates()) == 2

    def test_duplicates_are_correct_rows(self):
        dupes = _dedup().duplicates()
        assert {"city": "London", "country": "UK"} in dupes
        assert {"city": "Paris",  "country": "FR"} in dupes

    def test_no_dupes_returns_all(self):
        rows = [{"a": "1"}, {"a": "2"}, {"a": "3"}]
        result = CSVDeduplicator(iter(rows)).unique()
        assert len(result) == 3

    def test_empty_input(self):
        result = CSVDeduplicator(iter([])).unique()
        assert result == []


# ---------------------------------------------------------------------------
# key-based deduplication
# ---------------------------------------------------------------------------

class TestCSVDeduplicatorByKey:

    def test_dedup_by_single_key_count(self):
        # "London" appears twice with different countries -> only first kept
        result = CSVDeduplicator(iter(_rows_with_dupes()), keys=["city"]).unique()
        cities = [r["city"] for r in result]
        assert cities.count("London") == 1

    def test_dedup_by_single_key_total(self):
        result = CSVDeduplicator(iter(_rows_with_dupes()), keys=["city"]).unique()
        assert len(result) == 3  # London, Paris, Berlin

    def test_dedup_by_multiple_keys_same_as_full_row(self):
        result_keys = CSVDeduplicator(
            iter(_rows_with_dupes()), keys=["city", "country"]
        ).unique()
        result_full = CSVDeduplicator(iter(_rows_with_dupes())).unique()
        assert len(result_keys) == len(result_full)

    def test_duplicates_by_key(self):
        dupes = CSVDeduplicator(
            iter(_rows_with_dupes()), keys=["city"]
        ).duplicates()
        # London (UK dup) + Paris (FR dup) + London (DE — same city key)
        assert len(dupes) == 3
