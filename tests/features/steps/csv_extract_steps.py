from pathlib import Path
from behave import given, when, then, use_step_matcher
from src.csv_extract import Series1Pair, Extract
import csv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
use_step_matcher("parse")



# GIVEN steps
@given('a row with x123 "{x}" and y1 "{y}"')
def step_row_valid(context, x, y):
    """
    Create a valid row dictionary with x123 and y1 fields.

    Args:
        context: Behave context object.
        x: Value for the 'x123' field.
        y: Value for the 'y1' field.
    """
    context.row = {"x123": x, "y1": y}


@given('a row with missing x123 and y1')
def step_row_missing(context):
    """
    Create an empty row dictionary (missing required fields).

    Args:
        context: Behave context object.
    """
    context.row = {}


@given('a valid CSV file at "{path}"')
def step_valid_csv(context, path):
    """
    Create a valid CSV file at the given path with all required headers and a single data row.

    Args:
        context: Behave context object.
        path: Relative path where the CSV file will be created.
    """
    full_path = PROJECT_ROOT / path
    full_path.parent.mkdir(parents=True, exist_ok=True)

    with open(full_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["x123", "y1", "y2", "y3", "x4", "y4"]
        )
        writer.writeheader()
        writer.writerow({
            "x123": "1", "y1": "2",
            "y2": "3", "y3": "4",
            "x4": "5", "y4": "6",
        })

    context.csv_path = str(full_path)


@given('a non-existent CSV path "{path}"')
def step_missing_csv(context, path):
    """
    Set a CSV path that does not exist (no file is created).

    Args:
        context: Behave context object.
        path: Relative path to a non-existent CSV file.
    """
    context.csv_path = str(PROJECT_ROOT / path)


@given('a CSV file with missing headers at "{path}"')
def step_bad_headers(context, path):
    """
    Create a CSV file with only a subset of required headers (x123 and y1 only).

    Args:
        context: Behave context object.
        path: Relative path where the CSV file will be created.
    """
    full_path = PROJECT_ROOT / path
    full_path.parent.mkdir(parents=True, exist_ok=True)

    with open(full_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["x123", "y1"])
        writer.writeheader()
        writer.writerow({"x123": "1", "y1": "2"})

    context.csv_path = str(full_path)



# WHEN steps
@when('we build a pair using Series1Pair')
def step_build_pair(context):
    """
    Build a Series1Pair from the row stored in context.

    Args:
        context: Behave context object (must contain 'row' attribute).
    """
    builder = Series1Pair()
    context.pair = builder.from_row(context.row)   # no Extract needed here


@when('we extract pairs using Series1Pair')
def step_extract_pairs(context):
    """
    Extract pairs from the CSV file using Series1Pair and store the result.

    Args:
        context: Behave context object (must contain 'csv_path' attribute).
    """
    extractor = Extract(Series1Pair(), context.csv_path)
    context.result = extractor.build_pairs()


@when('we try to extract pairs')
def step_try_extract(context):
    """
    Attempt to extract pairs from the CSV file and capture any exception.

    Args:
        context: Behave context object (must contain 'csv_path' attribute).
    """
    extractor = Extract(Series1Pair(), context.csv_path)
    try:
        extractor.build_pairs()
        context.error = None
    except Exception as e:
        context.error = e


# THEN steps
@then('the pair should have x "{x_val}" and y "{y_val}"')
def step_pair_values(context, x_val, y_val):
    """
    Assert that the stored pair has the expected x and y values.

    Args:
        context: Behave context object (must contain 'pair' attribute).
        x_val: Expected x value.
        y_val: Expected y value.
    """
    assert context.pair.x == x_val, f"Expected x={x_val!r}, got {context.pair.x!r}"
    assert context.pair.y == y_val, f"Expected y={y_val!r}, got {context.pair.y!r}"


@then('the pair should have x "" and y ""')
def step_pair_empty(context):
    """
    Assert that the stored pair has empty string values for both x and y.

    Args:
        context: Behave context object (must contain 'pair' attribute).
    """
    assert context.pair.x == "", f"Expected x='', got {context.pair.x!r}"
    assert context.pair.y == "", f"Expected y='', got {context.pair.y!r}"


@then('we should get a list of pairs')
def step_check_list(context):
    """
    Assert that the extraction result is a non-empty list.

    Args:
        context: Behave context object (must contain 'result' attribute).
    """
    assert isinstance(context.result, list), "Result is not a list"
    assert len(context.result) > 0, "Result list is empty"


@then('an error should occur')
def step_check_error(context):
    """
    Assert that an error was captured during extraction.

    Args:
        context: Behave context object (must contain 'error' attribute).
    """
    assert context.error is not None, "Expected an error but none was raised"


@then('a header error should occur')
def step_check_header_error(context):
    """
    Assert that a header-related error (missing expected columns) occurred.

    Args:
        context: Behave context object (must contain 'error' attribute).
    """
    assert context.error is not None, "Expected an error but none was raised"
    assert "Missing expected columns" in str(context.error), (
        f"Expected 'Missing expected columns' in error, got: {context.error}"
    )