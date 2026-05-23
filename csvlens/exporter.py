import csv
import json
import io
from typing import Iterable, Iterator, Dict, Any, Optional


class CSVExporter:
    """
    Exports rows (dicts) from a CSVQuery or any iterable to various formats.
    Supports streaming export to CSV, JSON Lines, and JSON array.
    """

    def __init__(self, rows: Iterable[Dict[str, Any]]):
        self._rows = rows

    def to_csv(self, file_obj, fieldnames: Optional[list] = None) -> int:
        """
        Write rows as CSV to a file-like object.
        Returns the number of rows written.
        """
        rows_written = 0
        writer = None

        for row in self._rows:
            if writer is None:
                headers = fieldnames or list(row.keys())
                writer = csv.DictWriter(
                    file_obj, fieldnames=headers, extrasaction="ignore"
                )
                writer.writeheader()
            writer.writerow(row)
            rows_written += 1

        return rows_written

    def to_jsonl(self, file_obj) -> int:
        """
        Write rows as JSON Lines (one JSON object per line) to a file-like object.
        Returns the number of rows written.
        """
        rows_written = 0
        for row in self._rows:
            file_obj.write(json.dumps(row) + "\n")
            rows_written += 1
        return rows_written

    def to_json(self, file_obj, indent: Optional[int] = None) -> int:
        """
        Write all rows as a JSON array to a file-like object.
        Returns the number of rows written.
        """
        all_rows = list(self._rows)
        json.dump(all_rows, file_obj, indent=indent)
        return len(all_rows)

    def to_csv_string(self, fieldnames: Optional[list] = None) -> str:
        """Return CSV-formatted string of all rows."""
        buf = io.StringIO()
        self.to_csv(buf, fieldnames=fieldnames)
        return buf.getvalue()

    def to_jsonl_string(self) -> str:
        """Return JSON Lines formatted string of all rows."""
        buf = io.StringIO()
        self.to_jsonl(buf)
        return buf.getvalue()

    def to_json_string(self, indent: Optional[int] = None) -> str:
        """Return JSON array formatted string of all rows."""
        buf = io.StringIO()
        self.to_json(buf, indent=indent)
        return buf.getvalue()
