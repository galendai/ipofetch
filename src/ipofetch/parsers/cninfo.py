"""Parser for cninfo.com.cn (巨潮资讯网) prospectus pages."""

from typing import List

from ipofetch.parsers.base import BaseParser


class CninfoParser(BaseParser):
    """Parser for cninfo.com.cn prospectus pages."""

    def extract_pdf_links(self, url: str, html_content: str) -> List[str]:
        """Extract PDF download links from cninfo HTML content.

        Args:
            url: The original cninfo page URL
            html_content: HTML content of the page

        Returns:
            List of PDF download URLs

        Raises:
            ValueError: If the URL or HTML content is invalid
            RuntimeError: If parsing fails
        """
        # TODO: Implement cninfo-specific PDF link extraction logic
        # This is a placeholder implementation
        return []

    def is_supported_url(self, url: str) -> bool:
        """Check if the URL is a cninfo.com.cn URL.

        Args:
            url: The URL to check

        Returns:
            True if the URL is from cninfo.com.cn, False otherwise
        """
        return "cninfo.com.cn" in url.lower()
