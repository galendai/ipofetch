"""Main CLI entry point for IPO Prospectus Fetcher."""
from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel

from ipofetch import __version__
from ipofetch.core.api import download_prospectus_from_url


# Initialize Typer app and Rich console
app = typer.Typer(
    name="ipofetch",
    help="A lightweight Python CLI tool for downloading IPO prospectus PDFs from various exchanges.",
    add_completion=False,
    rich_markup_mode="rich",
)
console = Console(soft_wrap=True, legacy_windows=False)


def version_callback(value: bool) -> None:
    """Show version information and exit."""
    if value:
        console.print(
            f"[bold blue]IPOFetch[/bold blue] version [green]{__version__}[/green]"
        )
        raise typer.Exit


@app.command()
def main(
    url: str = typer.Argument(
        ...,
        help="URL of the prospectus page to download PDF from",
        metavar="URL",
    ),
    output: str | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Output directory for downloaded files (default: ./prospectus/)",
        metavar="DIR",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output mode",
    ),
    version: bool | None = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show version information and exit",
    ),
) -> None:
    """Download IPO prospectus PDF from the given URL.

    Supports China (cninfo), Hong Kong (HKEXnews), and US (SEC EDGAR) exchanges.

    Examples:
        ipofetch https://example.com/prospectus-page
        ipofetch https://example.com/prospectus-page --output ./downloads/
        ipofetch https://example.com/prospectus-page --verbose
    """
    # Mark version parameter as unused (handled by callback)
    del version

    # Set default output directory if not provided
    output_dir = output or "./prospectus/"

    if verbose:
        console.print(f"[dim]Starting download from: {url}[/dim]")
        console.print(f"[dim]Output directory: {output_dir}[/dim]")

    try:
        # Show welcome message
        console.print(
            Panel.fit(
                f"[bold blue]IPOFetch[/bold blue] v{__version__}\n"
                "Downloading IPO prospectus PDF...",
                border_style="blue",
            )
        )

        # Call the core download function
        result = download_prospectus_from_url(url, output_dir)

        if result["success"]:
            console.print("[green]✓[/green] Download completed successfully!")
            if verbose:
                console.print(f"[dim]PDF saved to: {result['pdf_path']}[/dim]")
                console.print(
                    f"[dim]Metadata saved to: {result['metadata_path']}[/dim]"
                )
                if "mapping_path" in result:
                    console.print(
                        f"[dim]PDF mapping saved to: {result['mapping_path']}[/dim]"
                    )
                console.print(f"[dim]File size: {result['file_size']} bytes[/dim]")
                console.print(
                    f"[dim]Download time: {result['download_time']:.2f}s[/dim]"
                )
        else:
            console.print("[red]✗[/red] Download failed!")
            if result.get("error"):
                console.print(f"[red]Error details:[/red] {result['error']}")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        if verbose:
            console.print_exception()
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
