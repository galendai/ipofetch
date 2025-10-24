"""Parser for HKEXnews prospectus pages."""
from __future__ import annotations

import re
from urllib.parse import urljoin
from urllib.parse import urlparse

from lxml import html

from ipofetch.parsers.base import BaseParser
from ipofetch.types import HKEXChapter


class HKEXNewsParser(BaseParser):
    """Parser for HKEXnews prospectus pages."""

    def extract_pdf_links(self, url: str, html_content: str) -> list[str]:
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

    def extract_chapters(self, url: str, html_content: str) -> list[HKEXChapter]:
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

            # Get base URL for relative links
            base_url = self._get_base_url(url)

            # Find all PDF links
            pdf_links = tree.xpath('//a[contains(@href, ".pdf")]')

            for i, link in enumerate(pdf_links, 1):
                href = link.get("href", "")
                text = link.text_content().strip()

                if not href or not text:
                    continue

                # Construct full PDF URL
                pdf_url = urljoin(base_url, href) if not href.startswith("http") else href

                chapter = HKEXChapter(
                    chapter_number=i,
                    chapter_title=self._generate_english_title(text, i),
                    chapter_title_original=text,
                    pdf_url=pdf_url,
                    relative_path=href
                )
                chapters.append(chapter)

        except Exception as e:
            msg = f"Failed to parse HKEXnews HTML content: {e}"
            raise RuntimeError(msg) from e
        else:
            return chapters

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

            # First try to extract from title (most reliable for HKEX pages)
            title_elements = tree.xpath("//title")
            if title_elements:
                title_text = title_elements[0].text_content().strip()
                # Extract company name from title (before stock code in parentheses)
                match = re.search(r"^(.+?)\s*\(\d{5}\)", title_text)
                if match:
                    company_name = match.group(1).strip()
                    # Remove common suffixes like " - 招股章程"
                    company_name = re.sub(r"\s*-\s*.+$", "", company_name)
                    if company_name:
                        return company_name

            # Look for company name in the specific font element with type="compName"
            company_elements = tree.xpath('//font[@type="compName"]')
            if company_elements:
                company_name = company_elements[0].text_content().strip()
                # Remove the " - B" suffix if present
                return re.sub(r"\s*-\s*[A-Z]$", "", company_name)

            # Fallback: look for bold text that might be company name
            bold_elements = tree.xpath("//b")
            for element in bold_elements:
                text = element.text_content().strip()
                if text and len(text) > 5:  # Reasonable company name length
                    # Remove the " - B" suffix if present
                    return re.sub(r"\s*-\s*[A-Z]$", "", text)

        except (ValueError, TypeError, AttributeError):
            pass

        return ""

    def extract_stock_code(self, html_content: str) -> str:
        """Extract stock code from HTML content.

        Args:
            html_content: HTML content of the page

        Returns:
            Stock code if found, empty string otherwise
        """
        if not html_content:
            return ""

        try:
            tree = html.fromstring(html_content)

            # Look for stock code patterns in various elements
            # Pattern 1: Look for 5-digit stock codes (e.g., 00853, 01234)
            text_content = tree.text_content()

            # Search for stock code patterns like "股份代號: 00853" or "Stock Code: 00853"
            stock_code_patterns = [
                r"股份代號[:\uff1a]\s*(\d{5})",  # Using Unicode escape for fullwidth colon
                r"股票代碼[:\uff1a]\s*(\d{5})",
                r"代號[:\uff1a]\s*(\d{5})",
                r"Stock\s+Code[:\uff1a]\s*(\d{5})",
                r"Code[:\uff1a]\s*(\d{5})",
                r"\((\d{5})\)",  # Stock code in parentheses
            ]

            for pattern in stock_code_patterns:
                match = re.search(pattern, text_content, re.IGNORECASE)
                if match:
                    return match.group(1)

            # Pattern 2: Look in title or meta tags
            title_elements = tree.xpath("//title")
            for element in title_elements:
                title_text = element.text_content().strip()
                match = re.search(r"\((\d{5})\)", title_text)
                if match:
                    return match.group(1)

            # Pattern 3: Look for stock code in table headers or cells
            table_cells = tree.xpath("//td | //th")
            for cell in table_cells:
                cell_text = cell.text_content().strip()
                if re.match(r"^\d{5}$", cell_text):
                    return cell_text

        except (ValueError, TypeError, AttributeError):
            pass

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

    def _extract_document_id(self, url: str) -> str | None:
        """Extract document ID from HKEXnews URL.

        Args:
            url: HKEXnews URL

        Returns:
            Document ID if found, None otherwise
        """
        # Pattern 1: /YYYY/MM/DD/XXXXXXXXXX_c.htm (document ID can be 10-13 digits)
        match = re.search(r"/(\d{10,13})_c\.htm", url)
        if match:
            return match.group(1)

        # Pattern 2: /ltnYYYYMMDDXXX_c.htm (like ltn20100913006_c.htm)
        match = re.search(r"/ltn(\d{11})_c\.htm", url)
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
        path_parts = parsed.path.rstrip("/").split("/")
        if path_parts and path_parts[-1].endswith(".htm"):
            path_parts = path_parts[:-1]

        base_path = "/".join(path_parts) + "/"
        return f"{parsed.scheme}://{parsed.netloc}{base_path}"

    def _generate_english_title(self, chinese_title: str, chapter_number: int) -> str:
        """Generate English filename from Chinese title.

        Args:
            chinese_title: Original Chinese chapter title
            chapter_number: Chapter number

        Returns:
            English filename suitable for filesystem
        """
        # Common chapter title mappings
        title_mappings = {
            "封面": "Cover",
            "目录": "Table_of_Contents",
            "概要": "Summary",
            "释义": "Definitions",
            "前瞻性陈述": "Forward_Looking_Statements",
            "风险因素": "Risk_Factors",
            "豁免严格遵守": "Waivers",
            "董事及参与全球发售的各方": "Directors_and_Parties",
            "公司资料": "Corporate_Information",
            "行业概览": "Industry_Overview",
            "监管概览": "Regulatory_Overview",
            "历史及发展": "History_and_Development",
            "业务": "Business",
            "与控股股东的关系": "Relationship_with_Controlling_Shareholders",
            "董事、监事及高级管理人员": "Directors_Supervisors_and_Senior_Management",
            "股本": "Share_Capital",
            "主要股东": "Substantial_Shareholders",
            "财务资料": "Financial_Information",
            "未来计划及所得款项用途": "Future_Plans_and_Use_of_Proceeds",
            "包销": "Underwriting",
            "全球发售的架构": "Structure_of_Global_Offering",
            "如何申请香港发售股份": "How_to_Apply_for_Hong_Kong_Offer_Shares",
            "附录": "Appendix",
            "会计师报告": "Accountants_Report",
            "未经审核备考财务资料": "Unaudited_Pro_Forma_Financial_Information",
            "物业估值": "Property_Valuation",
            "一般资料": "General_Information",
            "送呈文件": "Documents_Delivered",
            "法定及一般资料": "Statutory_and_General_Information"
        }

        # Try exact match first
        for chinese, english in title_mappings.items():
            if chinese in chinese_title:
                return english

        # If no match found, generate generic chapter name
        return f"Chapter_{chapter_number:02d}"
