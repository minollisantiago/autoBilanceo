import argparse
from rich.console import Console
from rich.table import Table

class RichArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.console = Console()

    def format_help(self):
        table = Table(
            show_header=True, 
            header_style="bold magenta",
            expand=False
        )
        table.add_column("Option", style="cyan")
        table.add_column("Description", style="green")
        table.add_column("Default", style="yellow")

        # Add program description
        self.console.print(f"\n[bold blue]🚀 {self.description}[/bold blue]\n")

        # Add usage
        self.console.print("[bold]Usage:[/bold]")
        self.console.print(f"  start [options]\n")

        # Add options to table
        for action in self._actions:
            if action.dest == 'help':
                continue  # Skip the default help action

            # Format option names
            option_str = ', '.join(action.option_strings)

            # Format default value
            default = action.default if action.default != argparse.SUPPRESS else ''

            # Add row to table
            table.add_row(
                option_str,
                action.help,
                str(default)
            )

        self.console.print(table)
        return ''  # Return empty string as the table is already printed

