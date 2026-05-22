"""Tests for csvlens.reader.CSVReader."""

from __future__ import annotations

import io
import textwrap

import pytest

from csvlens.reader import CSVReader


CSV_WITH_HEADER = textwrap.dedent("""\
    id,name,score
    1,Alice,95
    2,Bob,87
    3,Charlie,72
""")

CSV_NO_HEADER = textwrap.dedent("""\
    1,Alice,95
    2,Bob,87
""")

CSV_CUSTOM_DELIMITER = textwrap.dedent("""\
    id|name|score
    1|Alice|95
    2|Bob|87
""")


def _make_reader(content: str, **kwargs) -> CSVReader:
    return CSVReader(io.StringIO(content), **kwargs)


class TestCSVReaderWithHeader:
    def test_headers_parsed(self):
        reader = _make_reader(CSV_WITH_HEADER)
        list(reader.rows())  # consume to trigger header parsing
        assert reader.headers == ["id", "name", "score"]

    def test_row_count(self):
        reader = _make_reader(CSV_WITH_HEADER)
        rows = list(reader.rows())
        assert len(rows) == 3

    def test_rows_are_dicts(self):
        reader = _make_reader(CSV_WITH_HEADER)
        rows = list(reader.rows())
        assert all(isinstance(r, dict) for r in rows)

    def test_row_values(self):
        reader = _make_reader(CSV_WITH_HEADER)
        rows = list(reader.rows())
        assert rows[0] == {"id": "1", "name": "Alice", "score": "95"}
        assert rows[2]["name"] == "Charlie"

    def test_iter_protocol(self):
        rows = list(_make_reader(CSV_WITH_HEADER))
        assert len(rows) == 3

    def test_context_manager(self):
        with _make_reader(CSV_WITH_HEADER) as reader:
            rows = list(reader.rows())
        assert len(rows) == 3


class TestCSVReaderWithoutHeader:
    def test_headers_is_none(self):
        reader = _make_reader(CSV_NO_HEADER, has_header=False)
        list(reader.rows())
        assert reader.headers is None

    def test_rows_are_lists(self):
        reader = _make_reader(CSV_NO_HEADER, has_header=False)
        rows = list(reader.rows())
        assert all(isinstance(r, list) for r in rows)

    def test_row_values(self):
        reader = _make_reader(CSV_NO_HEADER, has_header=False)
        rows = list(reader.rows())
        assert rows[0] == ["1", "Alice", "95"]


class TestCSVReaderCustomDelimiter:
    def test_pipe_delimiter(self):
        reader = _make_reader(CSV_CUSTOM_DELIMITER, delimiter="|")
        rows = list(reader.rows())
        assert len(rows) == 2
        assert rows[1]["name"] == "Bob"


class TestCSVReaderEmptyFile:
    def test_empty_yields_nothing(self):
        reader = _make_reader("id,name\n")
        rows = list(reader.rows())
        assert rows == []
        assert reader.headers == ["id", "name"]

    def test_completely_empty(self):
        reader = _make_reader("", has_header=False)
        assert list(reader.rows()) == []
