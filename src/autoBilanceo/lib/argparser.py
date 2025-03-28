import argparse
from rich.console import Console
from rich.table import Table

class RichArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.console = Console()

    def format_help(self):
        # First table - Command options
        options_table = Table(
            show_header=True,
            header_style="bold magenta",
            expand=False
        )
        options_table.add_column("Option", style="cyan")
        options_table.add_column("Description", style="green")
        options_table.add_column("Default", style="yellow")

        # Add program description
        self.console.print(f"\n[bold blue]🚀 {self.description}[/bold blue]\n")

        # Add usage
        self.console.print("\n[bold]Available options for <start>:[/bold]")

        # Add options to table
        for action in self._actions:
            if action.dest == 'help':
                continue
            option_str = ', '.join(action.option_strings)
            default = action.default if action.default != argparse.SUPPRESS else ''
            options_table.add_row(option_str, action.help, str(default))

        self.console.print(options_table)

        # Add example usage section
        self.console.print("\n[bold]Example Usage:[/bold]")
        self.console.print(
            """
[dim]# Run with visible browser, 2 concurrent processes and 1.5s delay[/dim]
[bold green]uv run start --no-headless --max-concurrent 2 --delay 1.5[/bold green]

[dim]# Run quietly (less verbose) in headless mode[/dim]
[bold green]uv run start --quiet[/bold green]
            """
        )

        # Second table - Available tests
        self.console.print("\n[bold]🧪 Available Test Commands:[/bold]")
        self.console.print("\n[bold green]Run tests using:[/bold green] uv run <command>")
        tests_table = Table(
            show_header=True,
            header_style="bold magenta",
            expand=False
        )
        tests_table.add_column("Command", style="cyan")
        tests_table.add_column("Description", style="green")

        # Add test commands and their descriptions
        tests_table.add_row(
            "test_auth",
            "Test basic AFIP authentication"
        )
        tests_table.add_row(
            "test_comp_batch",
            "Test batch processing of multiple invoices"
        )
        tests_table.add_row(
            "test_comp_single",
            "Test single invoice processing"
        )
        tests_table.add_row(
            "test_comp_batch_complete",
            "Test complete batch processing workflow"
        )
        tests_table.add_row(
            "test_comp_single_complete",
            "Test complete single invoice workflow"
        )
        tests_table.add_row(
            "test_comp_nav",
            "Test navigation to invoice generator"
        )
        tests_table.add_row(
            "test_comp_type",
            "Test punto de venta and invoice type selection"
        )
        tests_table.add_row(
            "test_comp_form_1",
            "Test invoice issuance data form filling"
        )
        tests_table.add_row(
            "test_comp_form_2",
            "Test recipient form filling"
        )
        tests_table.add_row(
            "test_comp_form_3",
            "Test invoice content form filling"
        )

        self.console.print(tests_table)
        return ''

