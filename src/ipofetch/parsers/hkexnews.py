"""Parser for HKEXnews prospectus pages."""

from typing import List

from ipofetch.parsers.base import BaseParser


class HKEXNewsParser(BaseParser):
    """Parser for HKEXnews prospectus pages."""

    def extract_pdf_links(self, url: str, html_content: str) -> List[str]:
        """Extract PDF download links from HKEXnews HTML content.

        Args:
            url: The original HKEXnews page URL
            html_content: HTML content of the page

        Returns:
            List of PDF download URLs

        Raises:
            ValueError: If the URL or HTML content is invalid
            RuntimeError: If parsing fails
        """
        # TODO: Implement HKEXnews-specific PDF link extraction logic
        # This is a placeholder implementation
        return []

    def is_supported_url(self, url: str) -> bool:
        """Check if the URL is a HKEXnews URL.

        Args:
            url: The URL to check

        Returns:
            True if the URL is from HKEXnews, False otherwise
        """
        return "hkexnews.hk" in url.lower()
