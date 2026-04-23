import argparse
import json
import sys
from pathlib import Path

from csv_extract import (
    Extract,
    Series1Pair,
    Series2Pair,
    Series3Pair,
    Series4Pair,
)

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
            "csv_file",
            help="Path to input CSV file"
        )
        
        
        return parser.parse_args(argv, namespace=defaults)
        


class Main():
    """Main class orchestrating the CSV to JSON conversion process."""
    
    @staticmethod
    def main():
        """Execute the main CSV processing workflow."""
        warnings = []
        
        try:
            # Parse arguments
            args = GetOption.get_option(sys.argv[1:])
            output_dir = Path(args.output)
            csv_path = Path(args.csv_file)
            
            # Validate paths
            if not output_dir.exists():
                raise Exception(f"Output directory does not exist: {output_dir}")
            
            if not output_dir.is_dir():
                raise Exception(f"Output path is not a directory: {output_dir}")
            
            if not csv_path.exists():
                raise Exception(f"CSV file does not exists: {csv_path}")
            
            if not csv_path.is_file():
                raise Exception(f"CSV path is not a file: {csv_path}")
            
            # Check existing output files
            existing_files = []
            for i in range(1, 5):
                out_file = output_dir / f"series_{i}.json"
                if out_file.exists():
                    existing_files.append(out_file)
                    
            if existing_files:
                print("The following files already exists:")
                for f in existing_files:
                    print(f"  - {f}")
                response = input(f"Overwrite all? [y/N]: ")
                if response.strip().lower() != "y":
                    print("Aborted.")
                    sys.exit(0)
                        
            # Extraction
            series_data = []
            for series_class in args.series_classes:
                extractor = args.extract_class(series_class(), str(csv_path))
                pairs = extractor.build_pairs()
                series_data.append(pairs)
            
            
            # Write output
            for i, pairs in enumerate(series_data, start=1):
                output_file = output_dir / f"series_{i}.json"
                
                with open(output_file, "w", encoding="utf-8") as f:
                    for pair in pairs:
                        json_line = json.dumps(
                            {"x": pair.x, "y": pair.y}
                        )
                        f.write(json_line + "\n")
                    print(f"  Written: {output_file}")
                        
            # success message
            print("All series files written successfully.")
                        
            # warnings
            if warnings:
                print("\nWarnings")
                for w in warnings:
                    print(w)
                    
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
            
        except Exception as e:
            print(f"Unexpected error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    Main.main()