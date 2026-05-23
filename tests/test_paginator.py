import io
import pytest
from csvlens.reader import CSVReader
from csvlens.paginator import CSVPaginator
from csvlens.query import CSVQuery


CSV_DATA = """name,age,city
Alice,30,New York
Bob,25,London
Carol,35,Paris
Dave,28,Berlin
Eve,22,Tokyo
Frank,40,Sydney
Grace,31,Toronto
"""


def _rows():
    buf = io.StringIO(CSV_DATA)
    reader = CSVReader(buf)
    return iter(reader)


def _query():
    buf = io.StringIO(CSV_DATA)
    return CSVQuery(CSVReader(buf))


class TestCSVPaginatorBasic:
    def test_page_size_default(self):
        p = CSVPaginator(_rows())
        assert p.page_size == 100

    def test_custom_page_size(self):
        p = CSVPaginator(_rows(), page_size=3)
        assert p.page_size == 3

    def test_invalid_page_size(self):
        with pytest.raises(ValueError):
            CSVPaginator(_rows(), page_size=0)

    def test_invalid_page_number(self):
        p = CSVPaginator(_rows(), page_size=3)
        with pytest.raises(ValueError):
            p.get_page(0)

    def test_first_page_length(self):
        p = CSVPaginator(_rows(), page_size=3)
        page = p.get_page(1)
        assert len(page) == 3

    def test_second_page_length(self):
        p = CSVPaginator(_rows(), page_size=3)
        page = p.get_page(2)
        assert len(page) == 3

    def test_last_partial_page(self):
        p = CSVPaginator(_rows(), page_size=3)
        page = p.get_page(3)
        assert len(page) == 1

    def test_beyond_last_page_is_empty(self):
        p = CSVPaginator(_rows(), page_size=3)
        page = p.get_page(4)
        assert page == []

    def test_first_page_content(self):
        p = CSVPaginator(_rows(), page_size=3)
        page = p.get_page(1)
        assert page[0]["name"] == "Alice"
        assert page[2]["name"] == "Carol"

    def test_has_page_true(self):
        p = CSVPaginator(_rows(), page_size=3)
        assert p.has_page(1) is True
        assert p.has_page(3) is True

    def test_has_page_false(self):
        p = CSVPaginator(_rows(), page_size=3)
        assert p.has_page(4) is False

    def test_pages_iterator(self):
        p = CSVPaginator(_rows(), page_size=3)
        all_pages = list(p.pages())
        assert len(all_pages) == 3
        total_rows = sum(len(pg) for pg in all_pages)
        assert total_rows == 7

    def test_total_loaded_after_full_iteration(self):
        p = CSVPaginator(_rows(), page_size=3)
        list(p.pages())
        assert p.total_loaded() == 7


class TestQueryPaginate:
    def test_paginate_returns_paginator(self):
        p = _query().paginate(page_size=3)
        assert isinstance(p, CSVPaginator)

    def test_paginate_filtered(self):
        p = _query().where("city").equals("London").paginate(page_size=10)
        page = p.get_page(1)
        assert len(page) == 1
        assert page[0]["name"] == "Bob"

    def test_paginate_sorted(self):
        p = _query().order_by("name", ascending=True).paginate(page_size=3)
        page = p.get_page(1)
        assert page[0]["name"] == "Alice"
        assert page[1]["name"] == "Bob"
