"""csvlens-py: stream and lazily query large CSV files.

Modules:
    reader: Core CSV reading with lazy/streaming support via CSVReader.
    filter: Row-level filtering logic via RowFilter.
    query: High-level query interface via CSVQuery.

Typical usage::

    from csvlens import CSVQuery

    with CSVQuery("data.csv") as q:
        results = q.where("age > 30").select(["name", "age"]).fetch()
"""

from csvlens.reader import CSVReader
from csvlens.filter import RowFilter
from csvlens.query import CSVQuery

__all__ = ["CSVReader", "RowFilter", "CSVQuery"]
__version__ = "0.2.0"
