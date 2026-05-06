from unittest.mock import Mock, sentinel, call
from src.csv_extract import Series1Pair, Series2Pair, Series3Pair, Series4Pair


def test_series1pair_calls_target_class_correctly():
    """
    Test that Series1Pair.from_row extracts 'x123' and 'y1' from the row and
    passes them as x and y arguments respectively to the target class constructor.

    Verifies the mock calls and return value.
    """
    mock_class = Mock()
    
    builder = Series1Pair()
    builder.target_class = mock_class
    
    row = {
        "x123": sentinel.X,
        "y1": sentinel.Y
    }
    
    result = builder.from_row(row)
    
    assert mock_class.mock_calls == [
        call(x=sentinel.X, y=sentinel.Y)
    ]
    
    assert result == mock_class()
    
    
def test_series2pair_calls_target_class_correctly():
    """
    Test that Series2Pair.from_row extracts 'x123' and 'y2' from the row and
    passes them as x and y arguments respectively to the target class constructor.

    Verifies the mock calls and return value.
    """
    mock_class = Mock()
    
    builder = Series2Pair()
    builder.target_class = mock_class
    
    row = {
        "x123": sentinel.X,
        "y2": sentinel.Y
    }
    
    result = builder.from_row(row)
    
    assert mock_class.mock_calls == [
        call(x=sentinel.X, y=sentinel.Y)
    ]
    
    assert result == mock_class()
    
    
def test_series3pair_calls_target_class_correctly():
    """
    Test that Series3Pair.from_row extracts 'x123' and 'y3' from the row and
    passes them as x and y arguments respectively to the target class constructor.

    Verifies the mock calls and return value.
    """
    mock_class = Mock()
    
    builder = Series3Pair()
    builder.target_class = mock_class
    
    row = {
        "x123": sentinel.X,
        "y3": sentinel.Y
    }
    
    result = builder.from_row(row)
    
    assert mock_class.mock_calls == [
        call(x=sentinel.X, y=sentinel.Y)
    ]
    
    assert result == mock_class()
    
    
def test_series4pair_calls_target_class_correctly():
    """
    Test that Series4Pair.from_row extracts 'x4' and 'y4' from the row and
    passes them as x and y arguments respectively to the target class constructor.

    Verifies the mock calls and return value.
    """
    mock_class = Mock()
    
    builder = Series4Pair()
    builder.target_class = mock_class
    
    row = {
        "x4": sentinel.X,
        "y4": sentinel.Y
    }
    
    result = builder.from_row(row)
    
    assert mock_class.mock_calls == [
        call(x=sentinel.X, y=sentinel.Y)
    ]
    
    assert result == mock_class()