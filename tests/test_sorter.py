import io
import pytest
from csvlens.reader import CSVReader
from csvlens.sorter import CSVSorter


CSV_DATA = """name,age,city
Alice,30,New York
Bob,25,Los Angeles
Carol,35,Chicago
Dave,25,Houston
Eve,30,Phoenix
"""


def _rows():
    reader = CSVReader(io.StringIO(CSV_DATA))
    return list(reader)


class TestCSVSorterSingleKey:
    def test_sort_string_asc(self):
        sorter = CSVSorter(iter(_rows()))
        result = list(sorter.asc("name"))
        names = [r["name"] for r in result]
        assert names == sorted(names)

    def test_sort_string_desc(self):
        sorter = CSVSorter(iter(_rows()))
        result = list(sorter.desc("name"))
        names = [r["name"] for r in result]
        assert names == sorted(names, reverse=True)

    def test_sort_numeric_asc(self):
        sorter = CSVSorter(iter(_rows()))
        result = list(sorter.asc("age"))
        ages = [int(r["age"]) for r in result]
        assert ages == sorted(ages)

    def test_sort_numeric_desc(self):
        sorter = CSVSorter(iter(_rows()))
        result = list(sorter.desc("age"))
        ages = [int(r["age"]) for r in result]
        assert ages == sorted(ages, reverse=True)

    def test_sort_preserves_all_rows(self):
        sorter = CSVSorter(iter(_rows()))
        result = list(sorter.asc("name"))
        assert len(result) == 5


class TestCSVSorterNoKeys:
    def test_no_sort_keys_yields_original_order(self):
        original = _rows()
        sorter = CSVSorter(iter(original))
        result = list(sorter)
        assert [r["name"] for r in result] == [r["name"] for r in original]


class TestCSVSorterMultiKey:
    def test_multi_key_sort(self):
        sorter = CSVSorter(iter(_rows()))
        sorter.asc("age").asc("name")
        result = list(sorter)
        # Age 25: Bob, Dave — alphabetically Bob before Dave
        assert result[0]["name"] == "Bob"
        assert result[1]["name"] == "Dave"
        # Age 30: Alice, Eve
        assert result[2]["name"] == "Alice"
        assert result[3]["name"] == "Eve"
        # Age 35: Carol
        assert result[4]["name"] == "Carol"

    def test_order_by_chaining(self):
        sorter = CSVSorter(iter(_rows()))
        result = list(sorter.order_by("age").order_by("city", descending=True))
        assert len(result) == 5


class TestCSVSorterIterable:
    def test_iter_protocol(self):
        sorter = CSVSorter(iter(_rows()))
        sorter.asc("age")
        result = [row for row in sorter]
        assert len(result) == 5
