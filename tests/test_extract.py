import pytest
from src.csv_extract import Extract, Series1Pair
from unittest.mock import patch, mock_open, Mock



def test_validate_headers_success():
    """
    Test that _validate_headers does not raise an exception when all required headers are present.

    Verifies that a headers list containing all expected columns passes validation.
    """
    extractor = Extract(Series1Pair(), "dummy.csv")
    
    headers = ["x123", "y1", "y2", "y3", "x4", "y4"]
    
    # should not raise Error
    extractor._validate_headers(headers)
    
    
def test_validate_headers_missing():
    """
    Test that _validate_headers raises a ValueError when required headers are missing.

    Verifies that the exception message contains "Missing expected columns".
    """
    extractor = Extract(Series1Pair(), "dummy.csv")
    
    headers = ["x123", "y1"]
    
    with pytest.raises(ValueError) as e:
        extractor._validate_headers(headers)
        
    assert "Missing expected columns" in str(e.value)
    


def test_read_csv_success():
    """
    Test that _read_csv successfully reads and parses a valid CSV file.

    Verifies that the correct number of rows are returned and that values are properly extracted.
    """
    mock_csv = "x123,y1,y2,y3,x4,y4\n1,2,3,4,5,6\n"

    with patch("builtins.open", mock_open(read_data=mock_csv)):
        extractor = Extract(Series1Pair(), "dummy.csv")

        rows = extractor._read_csv()

        assert len(rows) == 1
        assert rows[0]["x123"] == "1"
        
def test_read_csv_file_not_found():
    """
    Test that _read_csv raises a ValueError when the CSV file does not exist.

    Verifies proper error handling for missing files.
    """
    extractor = Extract(Series1Pair(), "missing.csv")

    with pytest.raises(ValueError):
        extractor._read_csv()
        

def test_build_pairs_uses_builder():
    """
    Test that build_pairs correctly uses the builder to process each row from the CSV.

    Verifies that from_row is called for each row and that the returned pairs are collected.
    """
    mock_builder = Mock()

    mock_builder.from_row.return_value = "PAIR"

    fake_rows = [
        {"x123": "1", "y1": "2", "y2": "3", "y3": "4", "x4": "5", "y4": "6"},
        {"x123": "7", "y1": "8", "y2": "9", "y3": "10", "x4": "11", "y4": "12"},
    ]

    extractor = Extract(mock_builder, "fake.csv")

    with patch.object(extractor, "_read_csv", return_value=fake_rows):
        pairs = extractor.build_pairs()

    assert len(pairs) == 2
    assert mock_builder.from_row.call_count == 2