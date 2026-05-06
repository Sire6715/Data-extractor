from abc import ABC, abstractmethod
from src.model import RawData, XYPair
import csv
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

logger = logging.getLogger(__name__)

class PairBuilder(ABC):
    """Abstract base class for building XYPair objects from CSV rows."""

    target_class: type[RawData]
    
    @abstractmethod
    def from_row(self, row: list[str]) -> RawData:
        """Build an XYPair from a CSV row."""
        pass


class Series1Pair(PairBuilder):
    """Builds XYPair using x123 and y1 columns."""
    target_class = XYPair

    def from_row(self, row: dict[str, str]) -> RawData:
        """Extract x123 and y1 from row to create an XYPair."""
        
        cls = self.target_class
        try:
            x = row.get("x123")
            y = row.get("y1")

            if x is None or y is None:
                logger.warning(f"Missing value in row {row}")

            return cls(x=x or "", y=y or "")

        except Exception as e:
            logger.warning(f"Failed to process row {row}: {e}")
            return cls(x="", y="")


class Series2Pair(PairBuilder):
    """Builds XYPair using x123 and y2 columns."""
    target_class = XYPair
    
    def from_row(self, row: dict[str, str]) -> XYPair:
        """Extract x123 and y2 from row to create an XYPair."""
        
        cls = self.target_class
        try:
            x = row.get("x123")
            y = row.get("y2")

            if x is None or y is None:
                logger.warning(f"Missing value in row {row}")

            return cls(x=x or "", y=y or "")

        except Exception as e:
            logger.warning(f"Failed to process row {row}: {e}")
            return cls(x="", y="")


class Series3Pair(PairBuilder):
    """Builds XYPair using x123 and y3 columns."""
    target_class = XYPair
    
    def from_row(self, row: dict[str, str]) -> XYPair:
        """Extract x123 and y3 from row to create an XYPair."""
        
        cls = self.target_class
        try:
            x = row.get("x123")
            y = row.get("y3")

            if x is None or y is None:
                logger.warning(f"Missing value in row {row}")

            return cls(x=x or "", y=y or "")

        except Exception as e:
            logger.warning(f"Failed to process row {row}: {e}")
            return cls(x="", y="")


class Series4Pair(PairBuilder):
    """Builds XYPair using x4 and y4 columns."""
    target_class = XYPair
    
    def from_row(self, row: dict[str, str]) -> XYPair:
        """Extract x4 and y4 from row to create an XYPair."""
        
        cls = self.target_class
        try:
            x = row.get("x4")
            y = row.get("y4")

            if x is None or y is None:
                logger.warning(f"Missing value in row {row}")

            return cls(x=x or "", y=y or "")

        except Exception as e:
            logger.warning(f"Failed to process row {row}: {e}")
            return cls(x="", y="")


class Extract:
    """Extracts and builds XYPair objects from CSV files using a specified builder."""

    def __init__(self, builder: PairBuilder, file_path: str):
        """Initialize Extract with a PairBuilder and CSV file path."""
        self.builder = builder
        self.file_path = file_path

    def _read_csv(self) -> list[dict]:
        """Read CSV file and return list of dictionaries."""
        try:
            encoding = "utf-8"
            try:
                with open(self.file_path, "r", encoding=encoding) as file:
                    reader = csv.DictReader(file)
                    rows = list(reader)
            except UnicodeDecodeError:
                encoding = "latin-1"
                with open(self.file_path, "r", encoding=encoding) as file:
                    reader = csv.DictReader(file)
                    rows = list(reader)

            if not rows:
                msg = "Source file is empty: {self.file_path}"
                logger.debug(msg, exc_info=True)
                raise ValueError(msg)

        except FileNotFoundError:
            msg = f"Cannot read file:{self.file_path}. Check file Permissions."
            logger.debug(msg, exc_info=True)
            raise ValueError(msg)
        except Exception as e:
            logger.debug("Failed to read CSV: {e}")
            raise RuntimeError("Failed to read CSV: {e}") from e

        return rows

    def _validate_headers(self, headers: list[str]):
        """Validate that all expected CSV columns are present."""
        excepted = {"x123", "y1", "y2", "y3", "x4", "y4"}

        missing = excepted - set(headers)

        if missing:
            msg = f"Missing expected columns: {missing}. Found: {list(headers)}"
            logger.debug(msg)
            raise ValueError(msg)

    def build_pairs(self) -> list[RawData]:
        """Build and return a list of XYPair objects from the CSV file."""
        rows = self._read_csv()

        if not rows:
            msg = "No data found in CSV"
            logger.debug(msg)
            raise ValueError(msg)

        self._validate_headers(rows[0].keys())
        pairs = []

        for i, row in enumerate(rows):
            try:
                pair = self.builder.from_row(row)
                pairs.append(pair)
            except Exception as e:
                logger.warning(f"Skipping row {i} due to error {e}")

        return pairs
