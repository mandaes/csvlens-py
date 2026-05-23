"""Integration tests: CSVQuery chained with CSVTransformer."""
import io
import pytest
from csvlens.query import CSVQuery
from csvlens.transformer import CSVTransformer


CSV_DATA = """name,age,department
Alice,30,Engineering
Bob,25,Marketing
Carol,35,Engineering
Dave,28,Marketing
"""


def _query():
    return CSVQuery(io.StringIO(CSV_DATA))


class TestQueryTransformIntegration:
    def test_filter_then_transform(self):
        rows = _query().where("department").equals("Engineering").fetch()
        t = CSVTransformer(iter(rows)).apply("name", str.upper)
        result = t.to_list()
        assert len(result) == 2
        assert result[0]["name"] == "ALICE"
        assert result[1]["name"] == "CAROL"

    def test_transform_adds_field_after_filter(self):
        rows = _query().where("department").equals("Marketing").fetch()
        t = CSVTransformer(iter(rows)).add_field(
            "senior", lambda r: "yes" if int(r["age"]) >= 28 else "no"
        )
        result = t.to_list()
        names = {r["name"]: r["senior"] for r in result}
        assert names["Bob"] == "no"
        assert names["Dave"] == "yes"

    def test_transform_drop_field_after_filter(self):
        rows = _query().where("department").equals("Engineering").fetch()
        t = CSVTransformer(iter(rows)).drop_field("department")
        result = t.to_list()
        assert all("department" not in r for r in result)
        assert all("name" in r for r in result)

    def test_rename_field_after_filter(self):
        rows = _query().where("department").equals("Engineering").fetch()
        t = CSVTransformer(iter(rows)).rename("age", "years")
        result = t.to_list()
        assert "years" in result[0]
        assert "age" not in result[0]
