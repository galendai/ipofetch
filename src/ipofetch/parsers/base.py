"""Base parser module for extracting PDF links from web pages."""

from abc import ABC
from abc import abstractmethod
from typing import List


class BaseParser(ABC):
    """Abstract base class for URL parsers."""

    @abstractmethod
    def extract_pdf_links(self, url: str, html_content: str) -> List[str]:
        """Extract PDF download links from HTML content.

        Args:
            url: The original page URL
            html_content: HTML content of the page

        Returns:
            List of PDF download URLs

        Raises:
            ValueError: If the URL or HTML content is invalid
            RuntimeError: If parsing fails
        """

    @abstractmethod
    def is_supported_url(self, url: str) -> bool:
        """Check if the URL is supported by this parser.

        Args:
            url: The URL to check

        Returns:
            True if the URL is supported, False otherwise
        """


def extract_pdf_links(url: str, html_content: str) -> List[str]:
    """Generic function to extract PDF links from HTML content.

    This function provides a fallback implementation for extracting PDF links
    when no specific parser is available for the given URL.

    Args:
        url: The original page URL
        html_content: HTML content of the page

    Returns:
        List of PDF download URLs

    Raises:
        ValueError: If the URL or HTML content is invalid
        RuntimeError: If parsing fails
    """
    # TODO: Implement generic PDF link extraction logic
    # This is a placeholder implementation
    return []
