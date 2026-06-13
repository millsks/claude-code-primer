from logwatch.output import format_entry
from logwatch.watcher import LogEntry


def test_format_error_label() -> None:
    entry = LogEntry(line_number=1, content="connection failed", level="error")
    text = format_entry(entry)
    assert "ERROR" in text.plain
    assert "connection failed" in text.plain


def test_format_warning_label() -> None:
    entry = LogEntry(line_number=2, content="high memory usage", level="warning")
    text = format_entry(entry)
    assert "WARN" in text.plain
    assert "high memory usage" in text.plain


def test_format_info_label() -> None:
    entry = LogEntry(line_number=3, content="server started", level="info")
    text = format_entry(entry)
    assert "INFO" in text.plain
    assert "server started" in text.plain


def test_format_debug_label() -> None:
    entry = LogEntry(line_number=4, content="entering function", level="debug")
    text = format_entry(entry)
    assert "DEBUG" in text.plain
    assert "entering function" in text.plain


def test_format_unknown_label() -> None:
    entry = LogEntry(line_number=5, content="some random line", level="unknown")
    text = format_entry(entry)
    assert "some random line" in text.plain
