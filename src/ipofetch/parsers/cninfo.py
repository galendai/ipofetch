"""Parser for cninfo.com.cn (巨潮资讯网) prospectus pages."""
from __future__ import annotations

from ipofetch.parsers.base import BaseParser


class CninfoParser(BaseParser):
    """Parser for cninfo.com.cn prospectus pages."""

    def extract_pdf_links(self, url: str, html_content: str) -> list[str]:
        """Extract PDF download links from cninfo HTML content.

        Args:
            url: The original cninfo page URL (unused in current implementation)
            html_content: HTML content of the page (unused in current implementation)

        Returns:
            List of PDF download URLs

        Raises:
            ValueError: If the URL or HTML content is invalid
            RuntimeError: If parsing fails
        """
        # TODO: Implement cninfo-specific PDF link extraction logic
        # This is a placeholder implementation
        # Parameters are currently unused but kept for interface compatibility
        del url, html_content  # Explicitly mark as unused
        return []

    def is_supported_url(self, url: str) -> bool:
        """Check if the URL is a cninfo.com.cn URL.

        Args:
            url: The URL to check

        Returns:
            True if the URL is from cninfo.com.cn, False otherwise
        """
        return "cninfo.com.cn" in url.lower()
