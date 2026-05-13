# Data-Extractor
## Overview

Data-Extractor is a Python CLI tool that reads Anscombe's Quartet from a tab-separated CSV file and writes four Newline-Delimited JSON (NDJSON) files — one per data series.

[Anscombe's Quartet](https://en.wikipedia.org/wiki/Anscombe%27s_quartet) is a classic dataset of four series with nearly identical summary statistics but strikingly different visual distributions, making it a canonical example of why data visualisation matters.

The project is structured as a Python package following SOLID design principles with dependency injection, and includes unit tests (pytest), acceptance tests (Behave/BDD), and Sphinx-generated API documentation.

---

## Project Structure

```
Data-extractor/
├── src/
│   ├── __init__.py              # Required: marks src/ as a Python package
│   ├── acquire.py               # CLI entry point and orchestration (Main, GetOptions)
│   ├── csv_extract.py           # CSV parsing: Extract, Series1Pair–Series4Pair
│   └── model.py                 # Data models: XYPair, RawData
├── tests/
│   ├── test_acquire_cli.py      # Unit tests for acquire.py (mocked subprocess + Path)
│   ├── test_builders.py         # Unit tests for SeriesXPair builders
    |-- test_extract.py          # Unit test for extract function.
    |-- test_model.py            # Unit test for data model
    |
│   └── features/
│       ├── acquire.feature      # BDD feature: CLI end-to-end behaviour
│       ├── csv_extract.feature  # BDD feature: CSV extraction behaviour
│       └── steps/               # Behave step definitions
├── data/
|   |-- test_dir.csv/            # Test folder for test
│   └── Anscombe_quartet_data.csv  # Tab-separated input: x123, y1, y2, y3, x4, y4
├── output/
│   └── quartet/                 # Generated output (series_1.json – series_4.json)
├── docs/                        # Sphinx documentation source and build
├── pyproject.toml               # Project metadata and dependency extras
├── pytest.ini                   # Pytest config (pythonpath = .)
└── mypy.ini                     # MyPy type-checking config
```

> **Note:** `src/__init__.py` must exist (even if empty) for Python to treat `src/` as an importable package. Without it, both pytest and Sphinx will fail to import your modules.

---

## Installation

### Prerequisites

- Python 3.10 or higher
- pip

### Steps

1. Clone or download the project:
   ```bash
   git clone <https://github.com/Sire6715/Data-extractor.git>
   cd Data-extractor
   ```

2. Install with all development and test dependencies:
   ```bash
   pip install -e .[testdev,test]
   ```

   Or install dependencies individually if you don't use the extras:
   ```bash
   pip install sphinx furo sphinx-autodoc-typehints pytest behave
   ```

---

## Usage

Run the tool via the module entry point:

```bash
python -m src.acquire data/Anscombe_quartet_data.csv -o output/quartet
```

### CLI Arguments

| Argument | Required | Description |
|---|---|---|
| `--csv-path` | Yes | Path to the input tab-separated CSV file |
| `-o` | Yes | Directory where NDJSON output files will be written |
| `--force` | No | Overwrite existing output files without prompting. Without this flag, the tool will skip or warn if output files already exist. |

### Example Output

Each series produces a `.json` file with one JSON object per line (NDJSON format):

```json
{"x": 10.0, "y": 8.04}
{"x": 8.0, "y": 6.95}
{"x": 13.0, "y": 7.58}
```

> **Note on types:** `x` and `y` values are output as floats (not quoted strings). If your output shows `"x": "10.0"` with quotes, the values are being written as raw strings from the CSV rather than parsed numbers — check the `XYPair` model and `SeriesXPair.build()` for type conversion.

Four files are generated:

| File | Columns used |
|---|---|
| `series_1.json` | `x123`, `y1` |
| `series_2.json` | `x123`, `y2` |
| `series_3.json` | `x123`, `y3` |
| `series_4.json` | `x4`, `y4` |

Each series contains **11 data pairs**.

---

## Key Classes

| Class / Method | Module | Purpose |
|---|---|---|
| `Main.main()` | `acquire.py` | CLI entry point: validates paths, extracts series, writes files |
| `_validate_paths()` | `acquire.py` | Checks input file exists and output dir is writable |
| `_check_existing_files()` | `acquire.py` | Handles `--force` flag and skips/warns on existing output |
| `_extract_series()` | `acquire.py` | Delegates to `csv_extract` to build all four series |
| `_write_series()` | `acquire.py` | Writes NDJSON output files |
| `Extract` | `csv_extract.py` | Base class for CSV reading and series extraction |
| `Series1Pair` – `Series4Pair` | `csv_extract.py` | Concrete builders for each Anscombe series |
| `XYPair` | `model.py` | Single (x, y) data point |
| `RawData` | `model.py` | Holds raw CSV row data before transformation |

---

## Testing

### Unit tests (pytest)

```bash
pytest
```

Covers:
- `acquire.py`: CLI argument handling, path validation, file writing (subprocess and Path mocked)
- `csv_extract.py`: validators, readers, all four `SeriesXPair` builders

### Acceptance tests (Behave / BDD)

```bash
behave tests/features/
```

Feature files in `tests/features/` describe end-to-end behaviour in plain English (Gherkin). Step definitions live in `tests/features/steps/`.


### Run both together

```bash
pytest && behave tests/features/
```

---

## Logging

`acquire.py` uses Python's `logging` module throughout — there are no `print()` calls. The logger name is `data_extractor`. To see log output when running manually:

```bash
python -m src.acquire data/Anscombe_quartet_data.csv -o output/quartet
```

To control log level in your own scripts:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Building the Documentation

Sphinx is used to generate API documentation from docstrings.

```bash
cd docs
.\make.bat html        # Windows
# make html            # Linux/macOS
```

Open the result in your browser:

```
docs/build/html/index.html
```

To regenerate the `.rst` files after adding new modules:

```bash
sphinx-apidoc -o docs/source src/ -e --force
```

See the full [Sphinx documentation](https://www.sphinx-doc.org/en/master/tutorial/index.html) for configuration details.

---

## Dependencies

| Category | Packages |
|---|---|
| Core | None (pure Python standard library) |
| Testing | `pytest`, `behave`, `tox` |
| Type checking | `mypy` |
| Documentation | `sphinx`, `furo`, `sphinx-autodoc-typehints` |

To suppress mypy warnings about third-party libraries without type stubs (e.g. `behave`), add to `mypy.ini`:

```ini
[mypy-behave.*]
ignore_missing_imports = True
```

---

## Background: Anscombe's Quartet

The input CSV has the following tab-separated columns:

```
x123    y1    y2    y3    x4    y4
```

Series 1, 2, and 3 share the same `x` column (`x123`). Series 4 has its own `x` column (`x4`). Each series has 11 rows.

This shared-x structure is why `Series1Pair`, `Series2Pair`, and `Series3Pair` all read from `x123`, while `Series4Pair` reads from `x4`.

- see full API docs at docs/build/html/index.html
