import textwrap
from pathlib import Path

import pytest
from click.testing import CliRunner

from logwatch.cli import main


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def log_file(tmp_path: Path) -> Path:
    content = textwrap.dedent("""\
        INFO server started on port 8080
        WARNING disk usage at 85%
        ERROR failed to connect to database
    """)
    path = tmp_path / "app.log"
    path.write_text(content)
    return path


def test_scan_shows_all_levels(runner: CliRunner, log_file: Path) -> None:
    result = runner.invoke(main, ["--no-tail", str(log_file)])
    assert result.exit_code == 0
    assert "INFO" in result.output
    assert "WARN" in result.output
    assert "ERROR" in result.output


def test_filter_errors_only(runner: CliRunner, log_file: Path) -> None:
    result = runner.invoke(main, ["--no-tail", "--level", "error", str(log_file)])
    assert result.exit_code == 0
    assert "ERROR" in result.output
    assert "WARN" not in result.output
    assert "INFO " not in result.output


def test_filter_warnings_only(runner: CliRunner, log_file: Path) -> None:
    result = runner.invoke(main, ["--no-tail", "--level", "warning", str(log_file)])
    assert result.exit_code == 0
    assert "WARN" in result.output
    assert "ERROR" not in result.output


def test_summary_flag(runner: CliRunner, log_file: Path) -> None:
    result = runner.invoke(main, ["--summary", str(log_file)])
    assert result.exit_code == 0
    assert "Summary" in result.output
    assert "Errors" in result.output


def test_extra_pattern_filter(runner: CliRunner, log_file: Path) -> None:
    result = runner.invoke(main, ["--no-tail", "--pattern", "disk", str(log_file)])
    assert result.exit_code == 0
    assert "disk" in result.output
    assert "database" not in result.output


def test_missing_file(runner: CliRunner) -> None:
    result = runner.invoke(main, ["/nonexistent/file.log"])
    assert result.exit_code != 0


def test_version_option(runner: CliRunner) -> None:
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_help_option(runner: CliRunner) -> None:
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Watch a log FILE" in result.output
