"""Tests for the log file watcher and entry classification."""

import textwrap
import threading
import time
from pathlib import Path

import pytest

from logwatch.watcher import LogWatcher


@pytest.fixture
def log_file(tmp_path: Path) -> Path:
    """Write a five-line fixture log with one entry per level."""
    content = textwrap.dedent("""\
        2024-01-01 INFO server started
        2024-01-01 WARNING disk usage at 80%
        2024-01-01 ERROR connection refused
        2024-01-01 DEBUG processing request
        2024-01-01 some random line
    """)
    path = tmp_path / "test.log"
    path.write_text(content)
    return path


class TestDetectLevel:
    """Unit tests for LogWatcher.detect_level."""

    def test_error(self) -> None:
        assert LogWatcher.detect_level("ERROR: something failed") == "error"
        assert LogWatcher.detect_level("CRITICAL system failure") == "error"
        assert LogWatcher.detect_level("Unhandled Exception in thread") == "error"

    def test_warning(self) -> None:
        assert LogWatcher.detect_level("WARNING: high memory usage") == "warning"
        assert LogWatcher.detect_level("[WARN] slow query detected") == "warning"

    def test_info(self) -> None:
        assert LogWatcher.detect_level("INFO: server ready") == "info"

    def test_debug(self) -> None:
        assert LogWatcher.detect_level("DEBUG entering function foo") == "debug"

    def test_unknown(self) -> None:
        assert LogWatcher.detect_level("some untagged log line") == "unknown"

    def test_first_match_wins(self) -> None:
        # "error" is defined before "warning" in LEVEL_PATTERNS
        assert LogWatcher.detect_level("ERROR warning also present") == "error"


class TestScan:
    """Unit tests for LogWatcher.scan."""

    def test_all_lines(self, log_file: Path) -> None:
        entries = list(LogWatcher(log_file).scan())
        assert len(entries) == 5

    def test_last_n(self, log_file: Path) -> None:
        entries = list(LogWatcher(log_file).scan(last_n=2))
        assert len(entries) == 2
        assert "DEBUG" in entries[0].content

    def test_last_n_line_numbers(self, log_file: Path) -> None:
        entries = list(LogWatcher(log_file).scan(last_n=2))
        assert entries[0].line_number == 4
        assert entries[1].line_number == 5

    def test_all_line_numbers(self, log_file: Path) -> None:
        entries = list(LogWatcher(log_file).scan())
        assert entries[0].line_number == 1
        assert entries[4].line_number == 5

    def test_extra_pattern_match(self, log_file: Path) -> None:
        entries = list(LogWatcher(log_file, patterns=["disk"]).scan())
        assert len(entries) == 1
        assert "disk" in entries[0].content

    def test_extra_pattern_no_match(self, log_file: Path) -> None:
        entries = list(LogWatcher(log_file, patterns=["nonexistent"]).scan())
        assert entries == []

    def test_stats_after_full_scan(self, log_file: Path) -> None:
        watcher = LogWatcher(log_file)
        list(watcher.scan())
        assert watcher.stats.total == 5
        assert watcher.stats.errors == 1
        assert watcher.stats.warnings == 1
        assert watcher.stats.infos == 1
        assert watcher.stats.debugs == 1
        assert watcher.stats.unknowns == 1

    def test_levels_assigned_correctly(self, log_file: Path) -> None:
        entries = list(LogWatcher(log_file).scan())
        levels = {e.level for e in entries}
        assert levels == {"info", "warning", "error", "debug", "unknown"}


class TestTail:
    """Tests for LogWatcher.tail — real-file, threading-based."""

    def test_tail_yields_existing_lines_then_new(self, tmp_path: Path) -> None:
        """tail() first yields existing lines, then picks up appended content."""
        log_file = tmp_path / "app.log"
        log_file.write_text("INFO started\n")

        collected: list[str] = []

        def collect() -> None:
            watcher = LogWatcher(log_file)
            for entry in watcher.tail(last_n=1):
                collected.append(entry.content)
                if len(collected) >= 2:
                    return

        t = threading.Thread(target=collect, daemon=True)
        t.start()

        time.sleep(0.3)
        with log_file.open("a") as f:
            f.write("ERROR new failure\n")

        t.join(timeout=3.0)
        assert len(collected) == 2
        assert "started" in collected[0]
        assert "new failure" in collected[1]

    def test_tail_respects_extra_pattern(self, tmp_path: Path) -> None:
        """tail() filters new lines by extra pattern."""
        log_file = tmp_path / "app.log"
        log_file.write_text("")

        collected: list[str] = []

        def collect() -> None:
            watcher = LogWatcher(log_file, patterns=["timeout"])
            for entry in watcher.tail(last_n=0):
                collected.append(entry.content)
                if len(collected) >= 1:
                    return

        t = threading.Thread(target=collect, daemon=True)
        t.start()

        time.sleep(0.2)
        with log_file.open("a") as f:
            f.write("INFO ignored line\n")
            f.write("ERROR timeout occurred\n")

        t.join(timeout=3.0)
        assert len(collected) == 1
        assert "timeout" in collected[0]
