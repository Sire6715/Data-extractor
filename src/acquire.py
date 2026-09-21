import argparse
import json
import sys
from pathlib import Path
import logging
import csv
import io
import tempfile
import shutil
from src.kaggleclient import RestAccess
from src.zipfile import ZipFile


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
class Command:
    def execute(self):
        raise NotImplementedError

class LocalExtractCommand(Command):
    def __init__(self, args):
        self.args = args

    def execute(self):
        csv_path = Path(self.args.csv_file)
        output_dir = Path(self.args.output)
        Main._validate_paths(csv_path, output_dir)
        return csv_path, Main._extract_series(self.args, csv_path)

class ZipExtractCommand(Command):
    def __init__(self, args):
        self.args = args

    def execute(self):
        output_dir = Path(self.args.output)
        Main._validate_paths(None, output_dir)
        csv_path = Main._handle_zip(self.args)
        return csv_path, Main._extract_series(self.args, csv_path)


class SurveyCommand(Command):
    """
    Surveys Kaggle datasets using REST API pagination.
    """

    def __init__(self, args):
        self.args = args

    def execute(self):
        logger.info("Starting dataset survey mode...")

        rest = RestAccess(self.args.kaggle)

        url = "https://www.kaggle.com/api/v1/datasets/list"

        query = {}

        if self.args.search:
            query = {"search": self.args.search} if isinstance(self.args.search, str) else {}

        total = 0

        for dataset in rest.dataset_iter(url, query):

            total += 1

            # Safe field extraction (Kaggle datasets vary slightly)
            title = dataset.get("title", "N/A")
            ref = dataset.get("ref", "N/A")
            size = dataset.get("totalBytes", "N/A")

            logger.info(
                "Dataset: %s | Ref: %s | Size: %s",
                title,
                ref,
                size,
            )

        logger.info("Survey complete. Total datasets: %d", total)

        return None, None


class CommandFactory:
    @staticmethod
    def create(args):

        if args.search and args.kaggle:
            return SurveyCommand(args)

        if args.ref and args.kaggle:
            return ZipExtractCommand(args)

        if args.csv_file and not args.kaggle:
            return LocalExtractCommand(args)

        raise ValueError("Invalid argument combination")

class GetOption():
    """Handles command-line argument parsing for the CSV processing script."""
    
    @staticmethod
    def get_option(argv: list[str]) -> argparse.Namespace:
        """
        Parse command-line arguments.
        
        Args:
            argv: List of command-line arguments (typically sys.argv[1:]).
        
        Returns:
            argparse.Namespace: Parsed arguments with output, force, csv_file,
            kaggle, ref, search, extract_class, and series_classes attributes.
        """
        defaults = argparse.Namespace(
            extract_class=Extract,
            series_classes=[Series1Pair, Series2Pair, Series3Pair, Series4Pair]
        )
        
        parser = argparse.ArgumentParser(
            description="Process CSV into JSON series files",
            epilog="Example: python -m script  -o ./output data.csv"
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
        
        parser.add_argument(
            "-k",
            help='kaggle credentials file path (for --search mode)',
            dest="kaggle"
        )
        
        parser.add_argument(
            "--zip",
            help="Kaggle dataset reference (e.g. 'username/dataset-name') to download and process",
            dest="ref"
        )
        
        parser.add_argument(
            "--search",
            help="Search query for Kaggle datasets"
        )
        
        
        return parser.parse_args(argv, namespace=defaults)
        


class Main():
    """Main class orchestrating the CSV to JSON conversion process."""
    
    
    @staticmethod
    def _validate_paths(csv_path: Path, output_dir: Path):
        """
        Validate input CSV and output directory paths.
        
        Args:
            csv_path: Path to input CSV file.
            output_dir: Path to output directory.
        
        Returns:
            None
        
        Raises:
            SystemExit: If paths are invalid (exits with code 1).
        """
        if not output_dir.exists():
            logger.error(f"Output directory does not exist: {output_dir}")
            sys.exit(1)
            
        if not output_dir.is_dir():
            logger.error(f"Output path is not a directory: {output_dir}")
            sys.exit(1)
            
        if csv_path is not None and not csv_path.is_file():
            logger.error(f"CSV path is not a file: {csv_path}")
            sys.exit(1)

        
    @staticmethod
    def __check_existing_files(output_dir: Path, force: bool) -> bool:
        """
        
        Check for existing output files and handle overwrite confirmation.
        Args:
            output_dir: Directory where series_1-4.json files will be written.
            force: If True, skip confirmation and return True.
        
        Returns:
            bool: True if safe to proceed, False if user declines overwrite.
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
    def _extract_series(args, csv_path: Path) -> list:
        """
        Extract all four series from CSV using the configured extractor classes.
        
        Args:
            args: Namespace with extract_class, series_classes, and csv_file attributes.
        
        Returns:
            list: List of four series, each containing pairs of extracted x/y values.
        """
        logger.info("Extracting series data...")
        series_data = []
        
        for series_class in args.series_classes:
            extractor = args.extract_class(series_class(), str(csv_path))
            pairs = extractor.build_pairs()
            series_data.append(pairs)
            logger.debug(f"Extracted {len(pairs)} pairs from {series_class.__name__}")
            
        return series_data
    
    @staticmethod
    def _write_series(series_data: list, output_dir: Path):
        """
        Write each series to JSON files (JSON Lines format).
        
        Args:
            series_data: List of series data containing x/y pairs.
            output_dir: Directory to write series_1.json, series_2.json, etc.
        
        Returns:
            None
        """
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
    def _handle_zip(args) -> Path:
        """
        Extract CSV from ZIP and return temporary CSV path.
        """
        url = f"https://www.kaggle.com/api/v1/datasets/download/{args.ref}"
        zip_path = RestAccess(args.kaggle).get_zip(url)
        
        with ZipFile(zip_path) as archive:
            
            csv_members = [
                info for info in archive.infolist() 
                if info.filename.endswith(".csv")
            ]
            
            if not csv_members:
                logger.error("No CSV found inside ZIP")
                sys.exit(1)
                
            csv_members = csv_members[0]
            
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".csv"
            ) as tmp:
                
                with archive.open(csv_members) as source:
                    shutil.copyfileobj(source, tmp)
                    
                return Path(tmp.name)
    @staticmethod
    def main():
        """
        Execute the main CSV processing workflow.
        
        Returns:
            None (exits with code 0 on success, 1 on error)
        """
        print("SCRIPT STARTED")

        try:
            args = GetOption.get_option(sys.argv[1:])
            output_dir = Path(args.output)
 
            command = CommandFactory.create(args)
            csv_path, result = command.execute()

            if result:
                if not Main.__check_existing_files(output_dir, args.force):
                    sys.exit(0)

                Main._write_series(result, output_dir)

            logger.info("Completed successfully")

        except Exception as e:
            logger.exception(e)
            sys.exit(1)

                        
        except ValueError as e:
            logger.exception(f"Value error: {e}")
            sys.exit(1)
            
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            sys.exit(1)
        print("SCRIPT FINISHED")    


if __name__ == "__main__":
    Main.main()
