import re
import time
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

LEVEL_PATTERNS: dict[str, re.Pattern[str]] = {
    "error": re.compile(r"\b(error|err|critical|fatal|exception)\b", re.IGNORECASE),
    "warning": re.compile(r"\b(warning|warn)\b", re.IGNORECASE),
    "info": re.compile(r"\b(info|information)\b", re.IGNORECASE),
    "debug": re.compile(r"\b(debug|dbg)\b", re.IGNORECASE),
}


@dataclass
class LogEntry:
    line_number: int  # -1 for lines appended after tail() starts
    content: str
    level: str


@dataclass
class WatcherStats:
    total: int = 0
    errors: int = 0
    warnings: int = 0
    infos: int = 0
    debugs: int = 0
    unknowns: int = 0


class LogWatcher:
    def __init__(self, path: Path, patterns: list[str] | None = None) -> None:
        self.path = path
        self.extra_patterns: list[re.Pattern[str]] = [
            re.compile(p, re.IGNORECASE) for p in (patterns or [])
        ]
        self.stats = WatcherStats()

    @staticmethod
    def detect_level(line: str) -> str:
        for level, pattern in LEVEL_PATTERNS.items():
            if pattern.search(line):
                return level
        return "unknown"

    def _matches_extra(self, line: str) -> bool:
        if not self.extra_patterns:
            return True
        return any(p.search(line) for p in self.extra_patterns)

    def _make_entry(self, line_number: int, line: str) -> LogEntry:
        level = self.detect_level(line)
        self._update_stats(level)
        return LogEntry(line_number=line_number, content=line, level=level)

    def _update_stats(self, level: str) -> None:
        self.stats.total += 1
        match level:
            case "error":
                self.stats.errors += 1
            case "warning":
                self.stats.warnings += 1
            case "info":
                self.stats.infos += 1
            case "debug":
                self.stats.debugs += 1
            case _:
                self.stats.unknowns += 1

    def scan(self, last_n: int = 0) -> Iterator[LogEntry]:
        """Yield a LogEntry for each matching line. last_n=0 yields all lines."""
        lines = self.path.read_text().splitlines()
        if last_n > 0:
            offset = max(0, len(lines) - last_n)
            lines = lines[offset:]
            start = offset + 1
        else:
            start = 1
        for i, line in enumerate(lines, start=start):
            if self._matches_extra(line):
                yield self._make_entry(i, line)

    def tail(self, last_n: int = 10) -> Iterator[LogEntry]:
        """Yield existing lines then follow new content appended to the file."""
        yield from self.scan(last_n=last_n)
        with self.path.open() as f:
            f.seek(0, 2)  # jump to end of file
            while True:
                raw = f.readline()
                if raw:
                    line = raw.rstrip("\n")
                    if self._matches_extra(line):
                        yield self._make_entry(-1, line)
                else:
                    time.sleep(0.1)
