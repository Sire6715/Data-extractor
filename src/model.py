from dataclasses import dataclass
from typing import TypeAlias


@dataclass
class XYPair:
    x: str
    y: str
    
RawData: TypeAlias = XYPair
