"""HKEXnews API integration module."""

import asyncio
from pathlib import Path
from typing import Optional

import httpx
from rich.console import Console

from ipofetch.downloader.hkex_downloader import HKEXDownloader
from ipofetch.metadata.hkex_generator import HKEXMetadataGenerator
from ipofetch.parsers.hkexnews import HKEXNewsParser
from ipofetch.types import BatchResult
from ipofetch.types import DocumentMetadata


async def download_hkex_prospectus(
    url: str,
    output_dir: str = "./prospectus/",
    max_concurrent: int = 3,
    verbose: bool = False,
) -> DocumentMetadata:
    """Download HKEXnews prospectus with all chapters.

    Args:
        url: HKEXnews prospectus page URL
        output_dir: Output directory for downloaded files
        max_concurrent: Maximum concurrent downloads
        verbose: Enable verbose output

    Returns:
        DocumentMetadata with download results

    Raises:
        ValueError: If URL is not supported or invalid
        RuntimeError: If download fails
    """
    console = Console()
    
    if verbose:
        console.print(f"[bold blue]Starting HKEXnews prospectus download...[/bold blue]")
        console.print(f"URL: {url}")
        console.print(f"Output directory: {output_dir}")

    # Initialize components
    parser = HKEXNewsParser()
    downloader = HKEXDownloader(max_concurrent=max_concurrent)
    metadata_generator = HKEXMetadataGenerator()

    # Validate URL
    if not parser.is_supported_url(url):
        raise ValueError(f"URL is not supported by HKEXnews parser: {url}")

    try:
        # Fetch HTML content
        if verbose:
            console.print("[yellow]Fetching page content...[/yellow]")
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url)
            response.raise_for_status()
            html_content = response.text

        # Extract chapters
        if verbose:
            console.print("[yellow]Parsing chapters...[/yellow]")
        
        chapters = parser.extract_chapters(url, html_content)
        if not chapters:
            raise RuntimeError("No chapters found in the prospectus page")

        company_name = parser.extract_company_name(html_content)
        if not company_name:
            company_name = "Unknown Company"

        # Extract document ID
        document_id = parser._extract_document_id(url)
        if not document_id:
            raise RuntimeError("Cannot extract document ID from URL")

        if verbose:
            console.print(f"[green]Found {len(chapters)} chapters for {company_name}[/green]")
            console.print(f"Document ID: {document_id}")

        # Download all chapters
        if verbose:
            console.print("[yellow]Starting downloads...[/yellow]")

        batch_result = await downloader.download_all_chapters(
            chapters=chapters,
            output_dir=output_dir,
            company_name=company_name,
            document_id=document_id,
        )

        # Generate metadata
        if verbose:
            console.print("[yellow]Generating metadata...[/yellow]")

        document_metadata = metadata_generator.generate_document_metadata(
            document_id=document_id,
            company_name=company_name,
            original_url=url,
            chapters=chapters,
            batch_result=batch_result,
            output_dir=output_dir,
        )

        # Save metadata to file
        metadata_file = metadata_generator.save_metadata_to_file(
            metadata=document_metadata,
            output_dir=output_dir,
        )

        # Generate and save summary report
        summary_report = metadata_generator.generate_summary_report(
            metadata=document_metadata,
            batch_result=batch_result,
        )

        report_file = Path(output_dir) / f"{company_name}_{document_id}_report.txt"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(summary_report)

        if verbose:
            console.print(f"[green]Download completed![/green]")
            console.print(f"Metadata saved to: {metadata_file}")
            console.print(f"Report saved to: {report_file}")
            console.print(f"Success rate: {batch_result.successful_downloads}/{batch_result.total_chapters}")

        # Print summary
        console.print("\n" + summary_report)

        return document_metadata

    except httpx.HTTPError as e:
        raise RuntimeError(f"Failed to fetch page content: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Download failed: {e}") from e


def download_hkex_prospectus_sync(
    url: str,
    output_dir: str = "./prospectus/",
    max_concurrent: int = 3,
    verbose: bool = False,
) -> DocumentMetadata:
    """Synchronous wrapper for HKEXnews prospectus download.

    Args:
        url: HKEXnews prospectus page URL
        output_dir: Output directory for downloaded files
        max_concurrent: Maximum concurrent downloads
        verbose: Enable verbose output

    Returns:
        DocumentMetadata with download results

    Raises:
        ValueError: If URL is not supported or invalid
        RuntimeError: If download fails
    """
    return asyncio.run(
        download_hkex_prospectus(
            url=url,
            output_dir=output_dir,
            max_concurrent=max_concurrent,
            verbose=verbose,
        )
    )