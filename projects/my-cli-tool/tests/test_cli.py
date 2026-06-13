"""Tests for the logwatch CLI."""

import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from logwatch.cli import main
from logwatch.watcher import LogEntry, WatcherStats


@pytest.fixture
def runner() -> CliRunner:
    """Return a Click test runner."""
    return CliRunner()


@pytest.fixture
def log_file(tmp_path: Path) -> Path:
    """Write a three-line fixture log with info, warning, and error."""
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


def test_tail_mode_shows_entries(runner: CliRunner, log_file: Path) -> None:
    """Tail mode streams entries from watcher.tail() to stdout."""
    entries = [
        LogEntry(line_number=1, content="INFO server up", level="info"),
        LogEntry(line_number=2, content="ERROR db down", level="error"),
    ]
    mock_watcher = MagicMock()
    mock_watcher.tail.return_value = iter(entries)
    mock_watcher.stats = WatcherStats()

    with patch("logwatch.cli.LogWatcher", return_value=mock_watcher):
        result = runner.invoke(main, ["--tail", "-n", "2", str(log_file)])

    assert result.exit_code == 0
    assert "Watching" in result.output
    assert "ERROR" in result.output
    assert "INFO" in result.output


def test_keyboard_interrupt_shows_summary(runner: CliRunner, log_file: Path) -> None:
    """Ctrl+C during tail mode prints a summary and exits cleanly."""
    mock_watcher = MagicMock()
    mock_watcher.tail.side_effect = KeyboardInterrupt
    mock_watcher.stats = WatcherStats(total=3, errors=1, warnings=1, infos=1)

    with patch("logwatch.cli.LogWatcher", return_value=mock_watcher):
        result = runner.invoke(main, [str(log_file)])

    assert "Stopped" in result.output
    assert "Summary" in result.output
