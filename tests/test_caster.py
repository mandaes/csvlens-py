import pytest
from csvlens.caster import CSVCaster


def _rows():
    return [
        {"name": "Alice", "age": "30", "score": "9.5", "active": "true"},
        {"name": "Bob",   "age": "25", "score": "7.0", "active": "false"},
        {"name": "Carol", "age": "40", "score": "8.25", "active": "yes"},
        {"name": "Dave",  "age": "",   "score": "bad",  "active": "0"},
    ]


def _caster():
    return CSVCaster(_rows())


class TestCSVCasterInt:
    def test_cast_int_values(self):
        rows = CSVCaster(_rows()[:3]).as_int("age").rows()
        assert rows[0]["age"] == 30
        assert rows[1]["age"] == 25

    def test_cast_int_type(self):
        rows = CSVCaster(_rows()[:1]).as_int("age").rows()
        assert isinstance(rows[0]["age"], int)

    def test_cast_int_bad_value_raises(self):
        with pytest.raises(ValueError):
            CSVCaster(_rows()).as_int("age").rows()

    def test_cast_int_bad_value_uses_default(self):
        rows = CSVCaster(_rows()).as_int("age", default=0).rows()
        assert rows[3]["age"] == 0


class TestCSVCasterFloat:
    def test_cast_float_values(self):
        rows = CSVCaster(_rows()[:3]).as_float("score").rows()
        assert rows[0]["score"] == 9.5
        assert rows[2]["score"] == 8.25

    def test_cast_float_type(self):
        rows = CSVCaster(_rows()[:1]).as_float("score").rows()
        assert isinstance(rows[0]["score"], float)

    def test_cast_float_bad_value_uses_default(self):
        rows = CSVCaster(_rows()).as_float("score", default=-1.0).rows()
        assert rows[3]["score"] == -1.0


class TestCSVCasterBool:
    def test_true_strings(self):
        rows = CSVCaster(_rows()).as_bool("active").rows()
        assert rows[0]["active"] is True   # "true"
        assert rows[2]["active"] is True   # "yes"

    def test_false_strings(self):
        rows = CSVCaster(_rows()).as_bool("active").rows()
        assert rows[1]["active"] is False  # "false"
        assert rows[3]["active"] is False  # "0"


class TestCSVCasterCustom:
    def test_custom_fn(self):
        rows = CSVCaster(_rows()[:3]).as_type("name", str.upper).rows()
        assert rows[0]["name"] == "ALICE"

    def test_custom_fn_with_default(self):
        rows = (
            CSVCaster(_rows())
            .as_type("score", float, default=0.0)
            .rows()
        )
        assert rows[3]["score"] == 0.0


class TestCSVCasterChaining:
    def test_multiple_columns(self):
        rows = (
            CSVCaster(_rows()[:3])
            .as_int("age")
            .as_float("score")
            .as_bool("active")
            .rows()
        )
        assert isinstance(rows[0]["age"], int)
        assert isinstance(rows[0]["score"], float)
        assert isinstance(rows[0]["active"], bool)

    def test_uncasted_columns_unchanged(self):
        rows = CSVCaster(_rows()[:1]).as_int("age").rows()
        assert rows[0]["name"] == "Alice"

    def test_iter_protocol(self):
        caster = CSVCaster(_rows()[:2]).as_int("age")
        result = [row for row in caster]
        assert len(result) == 2
