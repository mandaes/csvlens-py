# csvlens-py

A Python library for streaming and lazily querying large CSV files without loading them into memory.

---

## Installation

```bash
pip install csvlens-py
```

---

## Usage

```python
from csvlens import CsvReader

# Stream rows lazily — no full file load
reader = CsvReader("large_file.csv")

# Iterate over rows one at a time
for row in reader.stream():
    print(row)

# Filter rows without loading the entire file
results = reader.query(where=lambda row: row["age"] > 30, limit=100)
for row in results:
    print(row)

# Fetch only specific columns
for row in reader.stream(columns=["name", "email"]):
    print(row)
```

### Key Features

- **Lazy evaluation** — rows are read on demand, not all at once
- **Memory efficient** — handles files larger than available RAM
- **Filtering & slicing** — query rows with conditions and limits
- **Column selection** — read only the columns you need
- **Standard CSV support** — works with any well-formed CSV file

---

## Requirements

- Python 3.8+
- No external dependencies (uses Python standard library only)

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on [GitHub](https://github.com/yourusername/csvlens-py).

---

## License

This project is licensed under the [MIT License](LICENSE).