import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "Anscombe_quartet_data.csv"


def run_command(args):
    """
    Execute the src.acquire module with the given arguments.

    Args:
        args: List of command-line arguments to pass to the acquire module.

    Returns:
        subprocess.CompletedProcess: The result of the subprocess run,
        containing returncode, stdout, and stderr.
    """
    result = subprocess.run(
        ["python", "-m", "src.acquire"] + args,
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT
    )
    return result


def test_successful_extraction(tmp_path):
    """
    Test that a successful extraction creates all four JSON files with correct content.

    Args:
        tmp_path: Pytest temporary path fixture.
    """
    output_dir = tmp_path / "test_quartet"
    output_dir.mkdir()

    result = run_command([
        "--force",
        "-o", str(output_dir),
        str(DATA_FILE)
    ])

    assert result.returncode == 0

    # Check files exist
    for i in range(1, 5):
        file = output_dir / f"series_{i}.json"
        assert file.exists()

    # Check file content
    content = (output_dir / "series_1.json").read_text()
    assert content.startswith('{"x": "10.0", "y": "8.04"}')

    # Check logs
    assert "All series files written successfully." in result.stderr


def test_output_directory_does_not_exist(tmp_path):
    """
    Test that the command fails when the output directory does not exist.

    Args:
        tmp_path: Pytest temporary path fixture.
    """
    output_dir = tmp_path / "output"

    result = run_command([
        "--force",
        "-o", str(output_dir),
        str(DATA_FILE)
    ])

    assert result.returncode != 0
    assert "Output directory does not exist:" in result.stderr


def test_unknown_option(tmp_path):
    """
    Test that the command fails when an unknown command-line option is provided.

    Args:
        tmp_path: Pytest temporary path fixture.
    """
    output_dir = tmp_path / "Anscombe_quartet_data.csv"
    output_dir.mkdir()

    result = run_command([
        "--unknown",
        str(DATA_FILE)
    ])

    assert result.returncode != 0


def test_csv_path_is_directory(tmp_path):
    """
    Test that the command fails when the provided CSV path is a directory, not a file.

    Args:
        tmp_path: Pytest temporary path fixture.
    """
    fake_csv_dir = tmp_path / "test_dir.csv"
    fake_csv_dir.mkdir()

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    result = run_command([
        "--force",
        "-o", str(output_dir),
        str(fake_csv_dir)
    ])

    assert result.returncode != 0
    assert "CSV path is not a file:" in result.stderr