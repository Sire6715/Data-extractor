from unittest.mock import sentinel
from dataclasses import asdict
from src.model import XYPair


def test_xypair():
    """
    Test that the XYPair dataclass correctly stores x and y values.

    Verifies:
    - The x attribute matches the provided value.
    - The y attribute matches the provided value.
    - The asdict conversion returns the expected dictionary representation.
    """
    pair = XYPair(x=sentinel.X, y=sentinel.Y)
    
    assert pair.x == sentinel.X
    assert pair.y == sentinel.Y
    assert asdict(pair) == {"x": sentinel.X, "y": sentinel.Y}