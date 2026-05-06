from pathlib import Path
import subprocess
from behave import given, when, then
import shutil
import shlex3

# ── Resolve paths relative to project root
PROJECT_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = PROJECT_ROOT


# ---- Given steps

@given('the "{path}" source file exists')
def step_source_file_exists(context, path):
    """
    Verify that a source file exists at the given path relative to the project root.

    Args:
        context: Behave context object.
        path: Relative path to the source file.
    """
    full_path = PROJECT_ROOT / path
    assert full_path.exists(), f"Source file not found: {full_path}"
    assert full_path.is_file(), f"Source path is not a file: {full_path}"



@given('the "{path}" directory does not exist')
def step_directory_not_exists(context, path):
    """
    Ensure that a directory does not exist at the given path. If it exists, delete it recursively.

    Args:
        context: Behave context object.
        path: Relative path to the directory.
    """
    full_path = PROJECT_ROOT / path

    if full_path.exists():
        shutil.rmtree(full_path) 

    assert not full_path.exists(), f"Expected directory to not exist: {full_path}"


@given('the "{path}" source path is a directory, not a file')
def step_source_path_is_directory(context, path):
    """
    Ensure that the given path is a directory. If it is a file, delete it and create a directory.

    Args:
        context: Behave context object.
        path: Relative path to convert into a directory.
    """
    full_path = PROJECT_ROOT / path
    if full_path.is_file():
        full_path.unlink()
    full_path.mkdir(parents=True, exist_ok=True)
    assert full_path.is_dir(), f"Expected a directory at: {full_path}"


@given('the "{path}" directory exists')
def step_directory_exists(context, path):
    """
    Ensure that a directory exists at the given path, creating it if necessary.

    Args:
        context: Behave context object.
        path: Relative path to the directory.
    """
    full_path = PROJECT_ROOT / path
    full_path.mkdir(parents=True, exist_ok=True)
    assert full_path.is_dir(), f"Directory not found: {full_path}"




# ---- When

@when('we run command "{command}"')
def step_run_command(context, command):
    """
    Execute a shell command in the project root directory, capturing stdout, stderr, and exit code.
    If the command references 'src/acquire.py', replace it with a module invocation using -m.

    Args:
        context: Behave context object.
        command: Shell command to execute.
    """
    # Replace script path invocation with module invocation
    parts = shlex.split(command)

    if "src/acquire.py" in parts:
        idx = parts.index("src/acquire.py")
        parts = parts[:idx] + ["-m", "src.acquire"] + parts[idx+1:]

    result = subprocess.run(
        parts,
        cwd=PROJECT_ROOT,   
        capture_output=True,
        text=True,
    )
    context.exit_code = result.returncode
    context.stdout = result.stdout
    context.stderr = result.stderr
    context.log = result.stdout + result.stderr


# ---- Then

@then('the "{path}" file exists')
def step_file_exists(context, path):
    """
    Assert that a file exists at the given path relative to the project root.

    Args:
        context: Behave context object.
        path: Relative path to the file.
    """
    full_path = PROJECT_ROOT / path
    assert full_path.exists(), f"Expected file not found: {full_path}"
    assert full_path.is_file(), f"Path exists but is not a file: {full_path}"


@then('the "{path}" file starts with \'{expected_line}\'')
def step_file_starts_with(context, path, expected_line):
    """
    Assert that the first line of the given file matches the expected line exactly.

    Args:
        context: Behave context object.
        path: Relative path to the file.
        expected_line: The exact line expected at the start of the file.
    """
    full_path = PROJECT_ROOT / path
    assert full_path.exists(), f"File not found: {full_path}"

    with open(full_path, "r", encoding="utf-8") as f:
        first_line = f.readline().strip()

    assert first_line == expected_line, (
        f"First line mismatch.\n"
        f"  Expected: {expected_line}\n"
        f"  Got:      {first_line}"
    )


@then('the log contains "{message}"')
def step_log_contains(context, message):
    """
    Assert that the captured log (stdout + stderr) contains the given message.

    Args:
        context: Behave context object.
        message: Substring expected to appear in the combined log output.
    """
    assert message in context.log, (
        f"Message not found in log.\n"
        f"  Looking for: {message}\n"
        f"  stdout: {context.stdout}\n"
        f"  stderr: {context.stderr}"
    )


@then('the exit code is not 0')
def step_exit_code_not_zero(context):
    """
    Assert that the exit code of the last executed command is non-zero.

    Args:
        context: Behave context object.
    """
    assert context.exit_code != 0, (
        f"Expected a non-zero exit code but got: {context.exit_code}\n"
        f"  stdout: {context.stdout}\n"
        f"  stderr: {context.stderr}"
    )