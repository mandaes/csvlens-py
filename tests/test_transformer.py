"""Tests for CSVTransformer."""
import io
import pytest
from csvlens.reader import CSVReader
from csvlens.transformer import CSVTransformer


CSV_DATA = """name,age,city
Alice,30,New York
Bob,25,London
Carol,35,Paris
"""


def _rows():
    reader = CSVReader(io.StringIO(CSV_DATA))
    return list(reader.rows())


def _transformer():
    reader = CSVReader(io.StringIO(CSV_DATA))
    return CSVTransformer(reader.rows())


class TestCSVTransformerApply:
    def test_apply_uppercase(self):
        t = _transformer().apply("name", str.upper)
        result = t.to_list()
        assert result[0]["name"] == "ALICE"
        assert result[1]["name"] == "BOB"

    def test_apply_does_not_affect_other_fields(self):
        t = _transformer().apply("name", str.upper)
        result = t.to_list()
        assert result[0]["city"] == "New York"

    def test_apply_missing_field_is_skipped(self):
        t = _transformer().apply("nonexistent", str.upper)
        result = t.to_list()
        assert result[0]["name"] == "Alice"  # unchanged

    def test_apply_chained(self):
        t = _transformer().apply("name", str.upper).apply("city", str.lower)
        result = t.to_list()
        assert result[0]["name"] == "ALICE"
        assert result[0]["city"] == "new york"


class TestCSVTransformerRename:
    def test_rename_field(self):
        t = _transformer().rename("name", "full_name")
        result = t.to_list()
        assert "full_name" in result[0]
        assert "name" not in result[0]

    def test_rename_preserves_value(self):
        t = _transformer().rename("name", "full_name")
        result = t.to_list()
        assert result[0]["full_name"] == "Alice"

    def test_rename_missing_field_is_noop(self):
        t = _transformer().rename("missing", "other")
        result = t.to_list()
        assert "other" not in result[0]


class TestCSVTransformerAddField:
    def test_add_computed_field(self):
        t = _transformer().add_field(
            "label", lambda row: f"{row['name']} ({row['city']})"
        )
        result = t.to_list()
        assert result[0]["label"] == "Alice (New York)"

    def test_add_field_present_in_all_rows(self):
        t = _transformer().add_field("tag", lambda row: "person")
        result = t.to_list()
        assert all(r["tag"] == "person" for r in result)


class TestCSVTransformerDropField:
    def test_drop_existing_field(self):
        t = _transformer().drop_field("age")
        result = t.to_list()
        assert "age" not in result[0]

    def test_drop_missing_field_is_noop(self):
        t = _transformer().drop_field("nonexistent")
        result = t.to_list()
        assert len(result) == 3  # rows still intact

    def test_remaining_fields_intact(self):
        t = _transformer().drop_field("age")
        result = t.to_list()
        assert "name" in result[0] and "city" in result[0]


class TestCSVTransformerIterable:
    def test_iter_yields_dicts(self):
        t = _transformer()
        for row in t:
            assert isinstance(row, dict)

    def test_original_rows_unchanged(self):
        rows = _rows()
        t = CSVTransformer(iter(rows)).apply("name", str.upper)
        _ = t.to_list()
        # Original list untouched because transformer copies each row
        assert rows[0]["name"] == "Alice"
