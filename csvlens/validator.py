from typing import Iterable, Iterator, Dict, Any, List, Callable, Optional


class CSVValidator:
    """
    Validates rows from a CSV stream against a set of user-defined rules.
    Produces per-row validation results without loading all data into memory.
    """

    def __init__(self, rows: Iterable[Dict[str, Any]]):
        self._rows = rows
        self._rules: List[Dict[str, Any]] = []

    def require(self, field: str) -> "CSVValidator":
        """Field must be present and non-empty."""
        self._rules.append({"type": "require", "field": field})
        return self

    def of_type(self, field: str, expected_type: type) -> "CSVValidator":
        """Field value must be castable to expected_type."""
        self._rules.append({"type": "of_type", "field": field, "expected": expected_type})
        return self

    def custom(self, field: str, fn: Callable[[str], bool], message: str = "custom rule failed") -> "CSVValidator":
        """Field value must satisfy a custom predicate."""
        self._rules.append({"type": "custom", "field": field, "fn": fn, "message": message})
        return self

    def _validate_row(self, row: Dict[str, Any], index: int) -> List[Dict[str, Any]]:
        errors = []
        for rule in self._rules:
            field = rule["field"]
            value = row.get(field, "")
            if rule["type"] == "require":
                if value is None or str(value).strip() == "":
                    errors.append({"row": index, "field": field, "error": "required field is empty"})
            elif rule["type"] == "of_type":
                try:
                    rule["expected"](value)
                except (ValueError, TypeError):
                    errors.append({
                        "row": index,
                        "field": field,
                        "error": f"cannot cast to {rule['expected'].__name__}"
                    })
            elif rule["type"] == "custom":
                try:
                    if not rule["fn"](value):
                        errors.append({"row": index, "field": field, "error": rule["message"]})
                except Exception as exc:
                    errors.append({"row": index, "field": field, "error": str(exc)})
        return errors

    def validate(self) -> Dict[str, Any]:
        """Run validation over all rows. Returns a summary with all errors."""
        all_errors: List[Dict[str, Any]] = []
        total = 0
        for index, row in enumerate(self._rows):
            total += 1
            all_errors.extend(self._validate_row(row, index))
        return {
            "total_rows": total,
            "error_count": len(all_errors),
            "valid": len(all_errors) == 0,
            "errors": all_errors,
        }

    def valid_rows(self) -> Iterator[Dict[str, Any]]:
        """Yield only rows that pass all validation rules."""
        for index, row in enumerate(self._rows):
            if not self._validate_row(row, index):
                yield row
