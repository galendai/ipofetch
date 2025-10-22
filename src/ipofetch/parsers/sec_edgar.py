"""Parser for SEC EDGAR prospectus pages."""
from __future__ import annotations

from ipofetch.parsers.base import BaseParser


class SECEdgarParser(BaseParser):
    """Parser for SEC EDGAR prospectus pages."""

    def extract_pdf_links(self, url: str, html_content: str) -> list[str]:
        """Extract PDF download links from SEC EDGAR HTML content.

        Args:
            url: The original SEC EDGAR page URL (unused in current implementation)
            html_content: HTML content of the page (unused in current implementation)

        Returns:
            List of PDF download URLs

        Raises:
            ValueError: If the URL or HTML content is invalid
            RuntimeError: If parsing fails
        """
        # TODO: Implement SEC EDGAR-specific PDF link extraction logic
        # This is a placeholder implementation
        # Parameters are currently unused but kept for interface compatibility
        del url, html_content  # Explicitly mark as unused
        return []

    def is_supported_url(self, url: str) -> bool:
        """Check if the URL is a SEC EDGAR URL.

        Args:
            url: The URL to check

        Returns:
            True if the URL is from SEC EDGAR, False otherwise
        """
        return "sec.gov" in url.lower()
