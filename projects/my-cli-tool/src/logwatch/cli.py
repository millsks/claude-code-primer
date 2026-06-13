"""Command-line interface for logwatch."""

import sys
from pathlib import Path

import click
from rich.console import Console

from logwatch import __version__
from logwatch.output import print_entry, print_summary
from logwatch.watcher import LogWatcher

console = Console()
err_console = Console(stderr=True)


@click.command()
@click.argument("file", type=click.Path(exists=True, readable=True, path_type=Path))
@click.option(
    "--pattern", "-p",
    multiple=True,
    metavar="REGEX",
    help="Extra regex pattern to match (repeatable).",
)
@click.option(
    "--tail/--no-tail", "-t/-T",
    default=True,
    show_default=True,
    help="Follow new lines in real-time (like tail -f).",
)
@click.option(
    "--lines", "-n",
    default=10,
    show_default=True,
    metavar="N",
    help="Number of existing lines to show before tailing.",
)
@click.option(
    "--level", "-l",
    type=click.Choice(["error", "warning", "info", "debug", "all"], case_sensitive=False),
    default="all",
    show_default=True,
    help="Show only lines matching this severity level.",
)
@click.option(
    "--summary/--no-summary", "-s/-S",
    default=False,
    help="Print a summary table after scanning (implies --no-tail).",
)
@click.version_option(version=__version__)
def main(
    file: Path,
    pattern: tuple[str, ...],
    tail: bool,
    lines: int,
    level: str,
    summary: bool,
) -> None:
    """Watch a log FILE for errors, warnings, and custom patterns."""
    watcher = LogWatcher(file, list(pattern))
    level_filter: str | None = None if level == "all" else level

    def passes(entry_level: str) -> bool:
        return level_filter is None or entry_level == level_filter

    try:
        if tail and not summary:
            console.print(f"[dim]Watching [bold]{file}[/bold] — Ctrl+C to stop[/dim]")
            for entry in watcher.tail(last_n=lines):
                if passes(entry.level):
                    print_entry(entry)
        else:
            for entry in watcher.scan():
                if passes(entry.level):
                    print_entry(entry)
            if summary:
                print_summary(watcher.stats, str(file))
    except KeyboardInterrupt:
        console.print("\n[dim]Stopped.[/dim]")
        print_summary(watcher.stats, str(file))
    except OSError as e:
        err_console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)
