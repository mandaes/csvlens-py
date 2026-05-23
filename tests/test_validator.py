import pytest
from csvlens.validator import CSVValidator


def _rows(data):
    return iter(data)


SAMPLE = [
    {"name": "Alice", "age": "30", "email": "alice@example.com"},
    {"name": "Bob", "age": "25", "email": "bob@example.com"},
    {"name": "", "age": "40", "email": "carol@example.com"},
    {"name": "Dave", "age": "abc", "email": "dave@example.com"},
    {"name": "Eve", "age": "22", "email": ""},
]


class TestCSVValidatorRequire:
    def test_no_errors_when_all_present(self):
        v = CSVValidator(_rows(SAMPLE[:2])).require("name")
        result = v.validate()
        assert result["valid"] is True
        assert result["error_count"] == 0

    def test_detects_empty_required_field(self):
        v = CSVValidator(_rows(SAMPLE)).require("name")
        result = v.validate()
        assert result["valid"] is False
        assert any(e["field"] == "name" for e in result["errors"])

    def test_multiple_required_fields(self):
        v = CSVValidator(_rows(SAMPLE)).require("name").require("email")
        result = v.validate()
        fields_with_errors = {e["field"] for e in result["errors"]}
        assert "name" in fields_with_errors
        assert "email" in fields_with_errors

    def test_total_rows_counted(self):
        v = CSVValidator(_rows(SAMPLE)).require("name")
        result = v.validate()
        assert result["total_rows"] == len(SAMPLE)


class TestCSVValidatorOfType:
    def test_valid_int_field(self):
        v = CSVValidator(_rows(SAMPLE[:2])).of_type("age", int)
        result = v.validate()
        assert result["valid"] is True

    def test_invalid_int_field(self):
        v = CSVValidator(_rows(SAMPLE)).of_type("age", int)
        result = v.validate()
        assert result["valid"] is False
        errors = [e for e in result["errors"] if e["field"] == "age"]
        assert len(errors) == 1
        assert "cannot cast" in errors[0]["error"]

    def test_error_row_index_is_correct(self):
        v = CSVValidator(_rows(SAMPLE)).of_type("age", int)
        result = v.validate()
        bad = [e for e in result["errors"] if e["field"] == "age"]
        assert bad[0]["row"] == 3  # Dave is at index 3


class TestCSVValidatorCustom:
    def test_custom_rule_passes(self):
        v = CSVValidator(_rows(SAMPLE[:2])).custom(
            "email", lambda v: "@" in v, "not a valid email"
        )
        result = v.validate()
        assert result["valid"] is True

    def test_custom_rule_fails(self):
        v = CSVValidator(_rows(SAMPLE)).custom(
            "email", lambda v: "@" in v, "not a valid email"
        )
        result = v.validate()
        assert result["valid"] is False
        errors = [e for e in result["errors"] if e["field"] == "email"]
        assert errors[0]["error"] == "not a valid email"


class TestCSVValidatorValidRows:
    def test_valid_rows_excludes_invalid(self):
        v = CSVValidator(_rows(SAMPLE)).require("name")
        valid = list(v.valid_rows())
        names = [r["name"] for r in valid]
        assert "" not in names

    def test_valid_rows_count(self):
        v = CSVValidator(_rows(SAMPLE)).require("name").of_type("age", int)
        valid = list(v.valid_rows())
        # Row with empty name (index 2) and row with bad age (index 3) are invalid
        assert len(valid) == 3
