"""Rich-based output formatting for logwatch."""

from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text

from logwatch.watcher import LogEntry, WatcherStats

console = Console()

LEVEL_STYLES: dict[str, str] = {
    "error": "bold red",
    "warning": "bold yellow",
    "info": "bold blue",
    "debug": "dim cyan",
    "unknown": "white",
}

LEVEL_LABELS: dict[str, str] = {
    "error": "ERROR",
    "warning": "WARN ",
    "info": "INFO ",
    "debug": "DEBUG",
    "unknown": "?????",
}


def format_entry(entry: LogEntry) -> Text:
    """Format a log entry as a Rich Text object with level-appropriate styling.

    Args:
        entry: The log entry to format.

    Returns:
        A Rich Text object with a styled level label and plain content.
    """
    style = LEVEL_STYLES.get(entry.level, "white")
    label = LEVEL_LABELS.get(entry.level, entry.level.upper()[:5])
    text = Text()
    text.append(f"[{label}] ", style=style)
    text.append(entry.content)
    return text


def print_entry(entry: LogEntry) -> None:
    """Print a single log entry to the console.

    Args:
        entry: The log entry to print.
    """
    console.print(format_entry(entry))


def print_summary(stats: WatcherStats, path: str) -> None:
    """Print a summary table of log level counts to the console.

    Args:
        stats: The collected counters from a LogWatcher session.
        path: The log file path to display in the table title.
    """
    table = Table(
        title=f"[bold]Log Summary: {path}[/bold]",
        box=box.ROUNDED,
        show_header=True,
    )
    table.add_column("Level", style="bold", min_width=10)
    table.add_column("Count", justify="right", min_width=6)
    table.add_row("Errors",   f"[bold red]{stats.errors}[/bold red]")
    table.add_row("Warnings", f"[bold yellow]{stats.warnings}[/bold yellow]")
    table.add_row("Info",     f"[bold blue]{stats.infos}[/bold blue]")
    table.add_row("Debug",    f"[dim cyan]{stats.debugs}[/dim cyan]")
    table.add_row("Unknown",  str(stats.unknowns))
    table.add_section()
    table.add_row("[bold]Total[/bold]", f"[bold]{stats.total}[/bold]")
    console.print(table)
