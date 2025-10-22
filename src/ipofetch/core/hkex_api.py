"""HKEXnews API integration module."""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING

import httpx
from rich.console import Console

from ipofetch.downloader.hkex_downloader import HKEXDownloader
from ipofetch.metadata.hkex_generator import HKEXMetadataGenerator
from ipofetch.parsers.hkexnews import HKEXNewsParser


if TYPE_CHECKING:
    from ipofetch.types import DocumentMetadata


async def _fetch_page_content(url: str, *, verbose: bool = False) -> str:
    """Fetch HTML content from the given URL.

    Args:
        url: The URL to fetch
        verbose: Whether to enable verbose output

    Returns:
        HTML content as string

    Raises:
        httpx.HTTPError: If HTTP request fails
    """
    console = Console(soft_wrap=True, legacy_windows=False)

    if verbose:
        console.print("[yellow]Fetching page content...[/yellow]")

    async with httpx.AsyncClient(
        timeout=30,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
    ) as client:
        response = await client.get(url)
        response.raise_for_status()
        
        # Handle encoding properly for Chinese content from HKEX
        # First check if charset is specified in Content-Type header
        content_type = response.headers.get('content-type', '').lower()
        detected_encoding = None
        
        # Extract charset from Content-Type header
        if 'charset=' in content_type:
            try:
                detected_encoding = content_type.split('charset=')[1].split(';')[0].strip('\"\'')
            except (IndexError, ValueError):
                pass
        
        # If no charset in headers, try to detect from HTML meta tags
        if not detected_encoding:
            content = response.content
            # Look for meta tags with charset or http-equiv
            if b'<meta' in content[:1000]:  # Check first 1000 bytes
                try:
                    # Try common Chinese encodings first for HKEX
                    for encoding in ['big5', 'gb2312', 'gbk', 'utf-8']:
                        try:
                            decoded = content.decode(encoding, errors='strict')
                            # Check if it contains valid Chinese characters
                            if any('\u4e00' <= char <= '\u9fff' for char in decoded[:2000]):
                                detected_encoding = encoding
                                break
                        except UnicodeDecodeError:
                            continue
                except Exception:
                    pass
        
        # Default to BIG5 for HKEX Traditional Chinese content
        if not detected_encoding:
            detected_encoding = 'big5'
        
        try:
            # Try to decode with detected encoding
            return response.content.decode(detected_encoding)
        except UnicodeDecodeError:
            # Fallback to BIG5 with replace errors for HKEX content
            return response.content.decode('big5', errors='replace')


def _extract_company_info(parser: HKEXNewsParser, html_content: str) -> tuple[str, str]:
    """Extract company name and original name from HTML content.

    Args:
        parser: HKEXNewsParser instance
        html_content: HTML content to parse

    Returns:
        Tuple of (company_name, company_name_original)
    """
    company_name = parser.extract_company_name(html_content)
    company_name_original = company_name  # Store original Chinese name
    if not company_name:
        company_name = "Unknown Company"
        company_name_original = "未知公司"

    return company_name, company_name_original


async def _process_download_and_metadata(
    downloader: HKEXDownloader,
    metadata_generator: HKEXMetadataGenerator,
    chapters: list,
    company_name: str,
    company_name_original: str,
    document_id: str,
    url: str,
    output_dir: str,
    *,
    verbose: bool = False,
) -> DocumentMetadata:
    """Process download and generate metadata.

    Args:
        downloader: HKEXDownloader instance
        metadata_generator: HKEXMetadataGenerator instance
        chapters: List of chapters to download
        company_name: Company name
        company_name_original: Original company name
        document_id: Document ID
        url: Original URL
        output_dir: Output directory
        verbose: Whether to enable verbose output

    Returns:
        DocumentMetadata with download results
    """
    console = Console()

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
        company_name_original=company_name_original,
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
    with report_file.open("w", encoding="utf-8") as f:
        f.write(summary_report)

    if verbose:
        console.print("[green]Download completed![/green]")
        console.print(f"Metadata saved to: {metadata_file}")
        console.print(f"Report saved to: {report_file}")
        console.print(f"Success rate: {batch_result.successful_downloads}/{batch_result.total_chapters}")

    # Print summary
    console.print("\n" + summary_report)

    return document_metadata


async def download_hkex_prospectus(
    url: str,
    output_dir: str = "./prospectus/",
    max_concurrent: int = 3,
    *,
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
        console.print("[bold blue]Starting HKEXnews prospectus download...[/bold blue]")
        console.print(f"URL: {url}")
        console.print(f"Output directory: {output_dir}")

    # Initialize components
    parser = HKEXNewsParser()
    downloader = HKEXDownloader(max_concurrent=max_concurrent)
    metadata_generator = HKEXMetadataGenerator()

    # Validate URL
    if not parser.is_supported_url(url):
        msg = f"URL is not supported by HKEXnews parser: {url}"
        raise ValueError(msg)

    try:
        # Fetch HTML content
        html_content = await _fetch_page_content(url, verbose=verbose)

        # Extract chapters
        if verbose:
            console.print("[yellow]Parsing chapters...[/yellow]")

        chapters = parser.extract_chapters(url, html_content)
        if not chapters:
            msg = "No chapters found in the prospectus page"
            raise RuntimeError(msg)

        # Extract company information
        company_name, company_name_original = _extract_company_info(parser, html_content)

        # Extract document ID
        document_id = parser._extract_document_id(url)
        if not document_id:
            msg = "Cannot extract document ID from URL"
            raise RuntimeError(msg)

        if verbose:
            console.print(f"[green]Found {len(chapters)} chapters for {company_name}[/green]")
            console.print(f"Document ID: {document_id}")

        # Process download and metadata generation
        return await _process_download_and_metadata(
            downloader=downloader,
            metadata_generator=metadata_generator,
            chapters=chapters,
            company_name=company_name,
            company_name_original=company_name_original,
            document_id=document_id,
            url=url,
            output_dir=output_dir,
            verbose=verbose,
        )

    except httpx.HTTPError as e:
        msg = f"Failed to fetch page content: {e}"
        raise RuntimeError(msg) from e
    except Exception as e:
        msg = f"Download failed: {e}"
        raise RuntimeError(msg) from e


def download_hkex_prospectus_sync(
    url: str,
    output_dir: str = "./prospectus/",
    max_concurrent: int = 3,
    *,
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
