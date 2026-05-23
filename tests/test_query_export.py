import io
import csv
import json
import pytest
from csvlens.reader import CSVReader
from csvlens.query import CSVQuery


CSV_DATA = """name,age,city
Alice,30,London
Bob,25,Paris
Carol,35,Berlin
Dave,25,London
"""


def _query():
    reader = CSVReader(io.StringIO(CSV_DATA))
    return CSVQuery(reader)


class TestQueryExport:
    def test_export_returns_exporter(self):
        from csvlens.exporter import CSVExporter
        exporter = _query().export()
        assert isinstance(exporter, CSVExporter)

    def test_export_all_rows_csv(self):
        result = _query().export().to_csv_string()
        lines = [l for l in result.strip().splitlines() if l]
        assert len(lines) == 5  # header + 4 rows

    def test_export_filtered_rows_csv(self):
        result = (
            _query()
            .where("city").equals("London")
            .export()
            .to_csv_string()
        )
        lines = [l for l in result.strip().splitlines() if l]
        assert len(lines) == 3  # header + Alice + Dave
        assert "Alice" in result
        assert "Dave" in result
        assert "Bob" not in result

    def test_export_filtered_rows_jsonl(self):
        result = (
            _query()
            .where("age").equals("25")
            .export()
            .to_jsonl_string()
        )
        lines = [l for l in result.strip().splitlines() if l]
        assert len(lines) == 2
        names = [json.loads(l)["name"] for l in lines]
        assert "Bob" in names
        assert "Dave" in names

    def test_export_filtered_rows_json(self):
        result = (
            _query()
            .where("city").contains("er")
            .export()
            .to_json_string()
        )
        data = json.loads(result)
        assert len(data) == 1
        assert data[0]["name"] == "Carol"

    def test_export_sorted_rows_csv(self):
        result = (
            _query()
            .order_by("name", ascending=True)
            .export()
            .to_csv_string()
        )
        reader = csv.DictReader(io.StringIO(result))
        names = [r["name"] for r in reader]
        assert names == sorted(names)
