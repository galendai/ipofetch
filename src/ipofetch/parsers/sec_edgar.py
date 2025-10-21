"""Parser for SEC EDGAR prospectus pages."""

from typing import List

from ipofetch.parsers.base import BaseParser


class SECEdgarParser(BaseParser):
    """Parser for SEC EDGAR prospectus pages."""

    def extract_pdf_links(self, url: str, html_content: str) -> List[str]:
        """Extract PDF download links from SEC EDGAR HTML content.

        Args:
            url: The original SEC EDGAR page URL
            html_content: HTML content of the page

        Returns:
            List of PDF download URLs

        Raises:
            ValueError: If the URL or HTML content is invalid
            RuntimeError: If parsing fails
        """
        # TODO: Implement SEC EDGAR-specific PDF link extraction logic
        # This is a placeholder implementation
        return []

    def is_supported_url(self, url: str) -> bool:
        """Check if the URL is a SEC EDGAR URL.

        Args:
            url: The URL to check

        Returns:
            True if the URL is from SEC EDGAR, False otherwise
        """
        return "sec.gov" in url.lower()
