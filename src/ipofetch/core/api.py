"""Core API module for IPO Prospectus Fetcher.

This module provides the main public API for downloading prospectus PDFs.
"""
from __future__ import annotations

from typing import Any

from ipofetch.core.hkex_api import download_hkex_prospectus_sync
from ipofetch.parsers.hkexnews import HKEXNewsParser


def download_prospectus_from_url(
    url: str, output_dir: str = "./prospectus/"
) -> dict[str, Any]:
    """Download prospectus PDF from the given URL.

    Args:
        url: The complete URL of the prospectus page
        output_dir: Output directory path, defaults to "./prospectus/"

    Returns:
        Dictionary containing download results:
        - success: Whether the download was successful
        - pdf_path: Path to the downloaded PDF file
        - metadata_path: Path to the generated metadata file
        - file_size: PDF file size in bytes
        - download_time: Download duration in seconds

    Raises:
        ValueError: If the URL is invalid or unsupported
        RuntimeError: If the download fails
    """
    # Check if URL is supported by HKEXnews parser
    hkex_parser = HKEXNewsParser()
    if not hkex_parser.is_supported_url(url):
        # TODO: Add support for other exchanges
        msg = f"URL is not supported by any available parser: {url}"
        raise ValueError(msg)

    try:
        # Use HKEXnews downloader
        metadata, download_time = download_hkex_prospectus_sync(
            url=url,
            output_dir=output_dir,
            verbose=True,
        )

        # Calculate total file size
        total_size = sum(
            chapter.file_size for chapter in metadata.chapters
            if chapter.file_size is not None
        )

        # Construct mapping file path
        mapping_path = f"./prospectus/{metadata.company_name}_{metadata.document_id}_mapping.json"

        return {
            "success": True,
            "pdf_path": f"./prospectus/{metadata.company_name}_{metadata.document_id}/",
            "metadata_path": f"./prospectus/{metadata.company_name}_{metadata.document_id}_metadata.json",
            "mapping_path": mapping_path,
            "file_size": total_size,
            "download_time": download_time,
        }
    except ValueError:
        # Re-raise ValueError as is (URL validation errors)
        raise
    except RuntimeError:
        # Re-raise RuntimeError as is (download errors)
        raise
    except Exception as e:
        # Convert other exceptions to RuntimeError
        msg = f"Unexpected error during download: {e}"
        raise RuntimeError(msg) from e
