import argparse
import json
import sys
from pathlib import Path
import logging

from src.csv_extract import (
    Extract,
    Series1Pair,
    Series2Pair,
    Series3Pair,
    Series4Pair,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

logger = logging.getLogger(__name__)

class GetOption():
    """Handles command-line argument parsing for the CSV processing script."""
    
    @staticmethod
    def get_option(argv: list[str]) -> argparse.Namespace:
        """Parse command-line arguments and return a Namespace object."""
        defaults = argparse.Namespace(
            extract_class=Extract,
            series_classes=[Series1Pair, Series2Pair, Series3Pair, Series4Pair]
        )
        
        parser = argparse.ArgumentParser(
            description="Process CSV into JSON series files",
            epilog="Example: python script.py -o ./output data.csv"
        )
        
        parser.add_argument(
            "-o",
            "--output",
            required=True,
            help="Output directory"
        )
        
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite files without prompting"
        )
        
        parser.add_argument(
            "csv_file",
            help="Path to input CSV file"
        )
        
        
        return parser.parse_args(argv, namespace=defaults)
        


class Main():
    """Main class orchestrating the CSV to JSON conversion process."""
    
    
    @staticmethod
    def _validate_paths(csv_path: Path, output_dir: Path):
        """Validate input and output, raising on any problem"""
        if not output_dir.exists():
            logger.error(f"Output directory does not exist: {output_dir}")
            sys.exit(1)
            
        if not output_dir.is_dir():
            logger.error(f"Output path is not a directory: {output_dir}")
            sys.exit(1)
            

        if not csv_path.is_file():
            logger.error(f"CSV path is not a file: {csv_path}")
            sys.exit(1)

    @staticmethod
    def __check_existing_files(output_dir: Path, force: bool) -> bool:
        """
        Warn about existing output files.
        Returns True if its safe to proceed, False if user declines overwrite.
        """
        existing_files = [
        output_dir / f"series_{i}.json"
        for i in range(1, 5)
        if (output_dir / f"series_{i}.json").exists()
    ] 

        if existing_files:
            logger.warning(f"{len(existing_files)} output file(s) already exist:")
            for f in existing_files:
                logger.warning(f"  - {f}")
                
        if force:
            return True
    
        response = input(f"Overwrite all? [y/N]: ")
        if response.strip().lower() != "y":
            logger.info("User aborted - overwrite declined.")
            return False
                    
        return True


    @staticmethod
    def _extract_series(args) -> list:
        """Extract all four series from the CSV."""
        logger.info("Extracting series data...")
        series_data = []
        
        for series_class in args.series_classes:
            extractor = args.extract_class(series_class(), str(args.csv_file))
            pairs = extractor.build_pairs()
            series_data.append(pairs)
            logger.debug(f"Extracted {len(pairs)} pairs from {series_class.__name__}")
            
        return series_data
    
    @staticmethod
    def _write_series(series_data: list, output_dir: Path):
        """Write each series """
        for i, pairs in enumerate(series_data, start=1):
            output_file = output_dir / f"series_{i}.json"
            
            with open(output_file, "w", encoding="utf-8") as f:
                for pair in pairs:
                    json_line = json.dumps(
                        {"x": pair.x, "y": pair.y}
                    )
                    f.write(json_line + "\n")
                logger.info(f"  Written: {output_file}")
                    
        # success message
        logger.info("All series files written successfully.")

    @staticmethod
    def main():
        """Execute the main CSV processing workflow."""
        print("SCRIPT STARTED")
        try:
            args = GetOption.get_option(sys.argv[1:])
            output_dir = Path(args.output)
            csv_path = Path(args.csv_file)
            force = args.force
            
            logger.info(f"Starting: {csv_path} -> {output_dir}")
            
            # Validate Path
            Main._validate_paths(csv_path, output_dir)
                
            if not Main.__check_existing_files(output_dir, force):
                sys.exit(0)
            
            # Extract data
            series_data = Main._extract_series(args)
            
            # Write data into file
            Main._write_series(series_data, output_dir)
            logger.info("All series files written successfully.")
                        
        except ValueError as e:
            logger.exception(f"Value error: {e}")
            sys.exit(1)
            
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            sys.exit(1)
        print("SCRIPT FINISHED")    


if __name__ == "__main__":
    Main.main()
    