"""Rich console output: panels, progress, and styled messages."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.theme import Theme

THEME = Theme(
    {
        "info": "cyan",
        "success": "bold green",
        "warning": "yellow",
        "error": "bold red",
        "muted": "dim",
        "accent": "bold magenta",
    }
)

console = Console(theme=THEME)


def print_banner() -> None:
    console.print(
        Panel.fit(
            "[accent]archforge[/accent] — opinionated architectural scaffolding",
            border_style="accent",
        )
    )


def print_success(title: str, message: str) -> None:
    console.print(Panel(message, title=f"[success]{title}[/success]", border_style="green"))


def print_error(title: str, message: str) -> None:
    console.print(Panel(message, title=f"[error]{title}[/error]", border_style="red"))


def print_warning(message: str) -> None:
    console.print(f"[warning]⚠[/warning]  {message}")


def print_info(message: str) -> None:
    console.print(f"[info]→[/info]  {message}")


def print_files_table(files: list[Path], title: str = "Generated files") -> None:
    if not files:
        return
    table = Table(title=title, show_header=True, header_style="bold")
    table.add_column("Path", style="cyan")
    for path in files:
        table.add_row(str(path))
    console.print(table)


def track_generation(steps: list[str]) -> None:
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating...", total=len(steps))
        for step in steps:
            progress.update(task, description=step)
            progress.advance(task)
