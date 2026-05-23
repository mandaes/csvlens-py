import io
import csv
import json
import pytest
from csvlens.exporter import CSVExporter


SAMPLE_ROWS = [
    {"name": "Alice", "age": "30", "city": "London"},
    {"name": "Bob", "age": "25", "city": "Paris"},
    {"name": "Carol", "age": "35", "city": "Berlin"},
]


def _exporter(rows=None):
    return CSVExporter(rows or SAMPLE_ROWS)


class TestCSVExporterToCSV:
    def test_csv_string_has_header(self):
        result = _exporter().to_csv_string()
        assert result.startswith("name,age,city")

    def test_csv_string_row_count(self):
        result = _exporter().to_csv_string()
        lines = [l for l in result.strip().splitlines() if l]
        assert len(lines) == 4  # header + 3 rows

    def test_csv_string_values(self):
        result = _exporter().to_csv_string()
        assert "Alice" in result
        assert "Bob" in result
        assert "Carol" in result

    def test_csv_custom_fieldnames_order(self):
        result = _exporter().to_csv_string(fieldnames=["city", "name"])
        first_line = result.splitlines()[0]
        assert first_line == "city,name"

    def test_csv_to_file_obj_returns_count(self):
        buf = io.StringIO()
        count = _exporter().to_csv(buf)
        assert count == 3

    def test_csv_empty_rows(self):
        result = CSVExporter([]).to_csv_string()
        assert result == ""


class TestCSVExporterToJSONL:
    def test_jsonl_line_count(self):
        result = _exporter().to_jsonl_string()
        lines = [l for l in result.strip().splitlines() if l]
        assert len(lines) == 3

    def test_jsonl_each_line_is_valid_json(self):
        result = _exporter().to_jsonl_string()
        for line in result.strip().splitlines():
            obj = json.loads(line)
            assert "name" in obj

    def test_jsonl_returns_count(self):
        buf = io.StringIO()
        count = _exporter().to_jsonl(buf)
        assert count == 3

    def test_jsonl_values(self):
        result = _exporter().to_jsonl_string()
        assert "Alice" in result
        assert "Paris" in result


class TestCSVExporterToJSON:
    def test_json_is_list(self):
        result = _exporter().to_json_string()
        data = json.loads(result)
        assert isinstance(data, list)
        assert len(data) == 3

    def test_json_values(self):
        result = _exporter().to_json_string()
        data = json.loads(result)
        names = [r["name"] for r in data]
        assert names == ["Alice", "Bob", "Carol"]

    def test_json_returns_count(self):
        buf = io.StringIO()
        count = _exporter().to_json(buf)
        assert count == 3

    def test_json_indent(self):
        result = _exporter().to_json_string(indent=2)
        assert "\n" in result
        data = json.loads(result)
        assert len(data) == 3
