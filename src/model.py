from dataclasses import dataclass
from typing import TypeAlias


@dataclass
class XYPair:
    """Represents a pair of x and y string values."""
    
    x: str
    """The x-coordinate or independent value."""
    
    y: str
    """The y-coordinate or dependent value."""
    
RawData: TypeAlias = XYPair
"""Type alias for XYPair representing raw data from CSV processing."""