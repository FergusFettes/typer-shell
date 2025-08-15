import os
import time
from datetime import datetime
from pathlib import Path

from rich import print
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from rich.table import Table
from typer import Context, Typer


def add_sample_commands(app: Typer):
    """Add sample utility commands to the shell"""

    @app.command(hidden=True)
    def shell(ctx: Context):
        """Drop into an ipython shell"""
        import IPython

        IPython.embed(globals_=globals())

    # File Operations
    @app.command()
    def ls(path: str = "."):
        """List directory contents"""
        p = Path(path)
        if not p.exists():
            print(f"[red]Path does not exist: {path}[/red]")
            return

        if p.is_file():
            print(f"[blue]{p.name}[/blue]")
            return

        items = []
        for item in sorted(p.iterdir()):
            if item.is_dir():
                items.append(f"[bold blue]{item.name}/[/bold blue]")
            else:
                items.append(f"[white]{item.name}[/white]")

        for item in items:
            print(item)

    @app.command()
    def cat(file_path: str):
        """Show file contents"""
        p = Path(file_path)
        if not p.exists():
            print(f"[red]File does not exist: {file_path}[/red]")
            return

        if p.is_dir():
            print(f"[red]Cannot cat directory: {file_path}[/red]")
            return

        try:
            content = p.read_text()
            print(content)
        except Exception as e:
            print(f"[red]Error reading file: {e}[/red]")

    @app.command()
    def pwd():
        """Show current working directory"""
        print(f"[bold green]{Path.cwd()}[/bold green]")

    # Rich Examples
    @app.command()
    def table():
        """Show a sample rich table"""
        table = Table(title="Sample Data")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Age", style="magenta")
        table.add_column("City", style="green")

        table.add_row("Alice", "25", "New York")
        table.add_row("Bob", "30", "San Francisco")
        table.add_row("Charlie", "35", "London")

        print(table)

    @app.command()
    def progress():
        """Show a progress bar demonstration"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            task = progress.add_task("Processing...", total=100)

            for _i in range(100):
                time.sleep(0.02)
                progress.update(task, advance=1)

    @app.command()
    def ask(question: str = "What's your name?"):
        """Interactive input prompt"""
        answer = Prompt.ask(question)
        print(f"[bold green]You answered: {answer}[/bold green]")

    @app.command()
    def panel(text: str = "Hello World!"):
        """Show text in a rich panel"""
        panel = Panel(text, title="Demo Panel", border_style="blue")
        print(panel)

    # System Info
    @app.command()
    def env(var: str):
        """Show environment variable"""
        value = os.getenv(var)
        if value:
            print(f"[bold green]{var}[/bold green]=[yellow]{value}[/yellow]")
        else:
            print(f"[red]Environment variable '{var}' not found[/red]")

    @app.command()
    def date():
        """Show current date and time"""
        now = datetime.now()
        print(f"[bold blue]{now.strftime('%Y-%m-%d %H:%M:%S')}[/bold blue]")
