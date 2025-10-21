"""Parser for HKEXnews prospectus pages."""

import re
from typing import List
from typing import Optional
from urllib.parse import urljoin
from urllib.parse import urlparse

from lxml import html

from ipofetch.parsers.base import BaseParser
from ipofetch.types import HKEXChapter


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
        chapters = self.extract_chapters(url, html_content)
        return [chapter.pdf_url for chapter in chapters]

    def extract_chapters(self, url: str, html_content: str) -> List[HKEXChapter]:
        """Extract chapter information from HKEXnews HTML content.

        Args:
            url: Original page URL
            html_content: HTML content of the page

        Returns:
            List of HKEXChapter objects

        Raises:
            RuntimeError: If parsing fails
        """
        if not html_content:
            return []

        try:
            tree = html.fromstring(html_content)
            chapters = []
            
            # Find all PDF links in the document
            pdf_links = tree.xpath('//a[contains(@href, ".pdf")]')
            
            for i, link in enumerate(pdf_links, 1):
                href = link.get('href', '').strip()
                text = link.text_content().strip()
                
                if not href or not text:
                    continue
                
                # Build absolute PDF URL
                base_url = self._get_base_url(url)
                if href.startswith('http'):
                    pdf_url = href
                else:
                    # Handle relative paths like "10556163/sehk22120700986_c.pdf"
                    pdf_url = urljoin(base_url, href)
                
                chapter = HKEXChapter(
                    chapter_number=i,
                    chapter_title=text,
                    pdf_url=pdf_url,
                    relative_path=href
                )
                chapters.append(chapter)
            
            return chapters

        except Exception as e:
            raise RuntimeError(f"Failed to parse HKEXnews HTML content: {e}") from e

    def extract_company_name(self, html_content: str) -> str:
        """Extract company name from HTML content.

        Args:
            html_content: HTML content of the page

        Returns:
            Company name if found, empty string otherwise
        """
        if not html_content:
            return ""

        try:
            tree = html.fromstring(html_content)
            
            # Look for company name in the specific font element with type="compName"
            company_elements = tree.xpath('//font[@type="compName"]')
            if company_elements:
                company_name = company_elements[0].text_content().strip()
                # Remove the " - B" suffix if present
                company_name = re.sub(r'\s*-\s*[A-Z]$', '', company_name)
                return company_name
            
            # Fallback: look for bold text that might be company name
            bold_elements = tree.xpath('//b')
            for element in bold_elements:
                text = element.text_content().strip()
                if text and len(text) > 5:  # Reasonable company name length
                    # Remove the " - B" suffix if present
                    text = re.sub(r'\s*-\s*[A-Z]$', '', text)
                    return text
            
            return ""

        except Exception:
            return ""

    def get_expected_chapter_count(self) -> int:
        """Get expected chapter count for HKEXnews documents.

        Returns:
            Expected number of chapters (typically 15-25)
        """
        return 25  # Maximum expected chapters

    def is_supported_url(self, url: str) -> bool:
        """Check if the URL is a HKEXnews URL.

        Args:
            url: The URL to check

        Returns:
            True if the URL is from HKEXnews, False otherwise
        """
        return "hkexnews.hk" in url.lower()

    def _extract_document_id(self, url: str) -> Optional[str]:
        """Extract document ID from HKEXnews URL.

        Args:
            url: HKEXnews URL

        Returns:
            Document ID if found, None otherwise
        """
        # Pattern: /YYYY/MM/DD/XXXXXXXXXX_c.htm (document ID can be 10-13 digits)
        match = re.search(r'/(\d{10,13})_c\.htm', url)
        if match:
            return match.group(1)
        return None

    def _get_base_url(self, url: str) -> str:
        """Get base URL for constructing absolute PDF URLs.

        Args:
            url: Original page URL

        Returns:
            Base URL for PDF construction
        """
        parsed = urlparse(url)
        # Remove the filename part to get directory URL
        path_parts = parsed.path.rstrip('/').split('/')
        if path_parts and path_parts[-1].endswith('.htm'):
            path_parts = path_parts[:-1]
        
        base_path = '/'.join(path_parts) + '/'
        return f"{parsed.scheme}://{parsed.netloc}{base_path}"
