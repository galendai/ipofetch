"""HKEXnews specific downloader for chapter-based PDF downloads."""
from __future__ import annotations

import asyncio
import random
import time
from pathlib import Path

import httpx
from rich.console import Console
from rich.progress import BarColumn
from rich.progress import Progress
from rich.progress import TextColumn
from rich.progress import TimeRemainingColumn

from ipofetch.types import BatchResult
from ipofetch.types import DownloadResult
from ipofetch.types import HKEXChapter


class HKEXDownloader:
    """港交所招股说明书下载器."""

    def __init__(
        self,
        max_concurrent: int = 3,
        max_retries: int = 3,
        timeout: int = 30,
        user_agent: str = "IPOFetch/1.0.0 (Research Tool; Contact: research@example.com)",
    ) -> None:
        """Initialize HKEXDownloader.

        Args:
            max_concurrent: Maximum concurrent downloads
            max_retries: Maximum retry attempts per chapter
            timeout: Request timeout in seconds
            user_agent: User agent string for requests
        """
        self.max_concurrent = max_concurrent
        self.max_retries = max_retries
        self.timeout = timeout
        self.user_agent = user_agent
        self.console = Console(soft_wrap=True, legacy_windows=False)

    async def download_chapter(
        self,
        chapter: HKEXChapter,
        output_dir: str,
        company_name: str,
        document_id: str,
        stock_code: str = "",
    ) -> DownloadResult:
        """Download a single chapter.

        Args:
            chapter: Chapter information
            output_dir: Output directory path
            company_name: Company name for file naming
            document_id: Document ID for file naming
            stock_code: Stock code for file naming

        Returns:
            DownloadResult with download status and metadata
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate filename with new naming convention: 股票代码-公司名称-章节序号-章节名称-下载文件时间戳.pdf
        safe_company_name = self._sanitize_filename(company_name)
        safe_chapter_title = self._sanitize_filename(chapter.chapter_title_original)  # Use original Chinese title

        # Generate timestamp for filename in UTC format (suitable for users in different time zones)
        import datetime
        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H%M%S") + "UTC"

        # Use stock code if available, otherwise use document_id as fallback
        code_prefix = stock_code if stock_code else document_id

        filename = f"{code_prefix}-{safe_company_name}-{chapter.chapter_number:02d}-{safe_chapter_title}-{timestamp}.pdf"
        file_path = output_path / filename

        # Skip if file already exists
        if file_path.exists():
            return DownloadResult(
                success=True,
                pdf_path=str(file_path),
                metadata_path="",
                file_size=file_path.stat().st_size,
                download_time=0.0,
                error_message=None,
            )

        start_time = time.time()

        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(
                    timeout=httpx.Timeout(30.0, connect=10.0),
                    headers={
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        "Accept": "application/pdf,application/octet-stream,*/*;q=0.8",
                        "Accept-Language": "en-US,en;q=0.5",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Connection": "keep-alive",
                        "Referer": "https://www1.hkexnews.hk/",
                        "Sec-Fetch-Dest": "document",
                        "Sec-Fetch-Mode": "navigate",
                        "Sec-Fetch-Site": "same-origin",
                    },
                    follow_redirects=True,
                ) as client:
                    response = await client.get(chapter.pdf_url)
                    response.raise_for_status()

                    # Write file
                    with Path(file_path).open("wb") as f:
                        f.write(response.content)

                    download_time = time.time() - start_time
                    file_size = len(response.content)

                    return DownloadResult(
                        success=True,
                        pdf_path=str(file_path),
                        metadata_path="",
                        file_size=file_size,
                        download_time=download_time,
                        error_message=None,
                    )

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    # Chapter doesn't exist, don't retry
                    return DownloadResult(
                        success=False,
                        pdf_path="",
                        metadata_path="",
                        file_size=0,
                        download_time=time.time() - start_time,
                        error_message=f"Chapter not found (404): {chapter.pdf_url}",
                    )
                if e.response.status_code == 429:
                    # Rate limited, wait longer
                    wait_time = 60 * (attempt + 1)
                    await asyncio.sleep(wait_time)
                    continue
                # Other HTTP errors, retry with exponential backoff
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
                continue

            except Exception as e:
                # Network or other errors, retry with exponential backoff
                f"Attempt {attempt + 1}/{self.max_retries}: {type(e).__name__}: {e!s}"

                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
                if attempt == self.max_retries - 1:
                    return DownloadResult(
                        success=False,
                        pdf_path="",
                        metadata_path="",
                        file_size=0,
                        download_time=time.time() - start_time,
                        error_message=f"Failed after {self.max_retries} attempts: {e!s}",
                    )

        # Should not reach here
        return DownloadResult(
            success=False,
            pdf_path="",
            metadata_path="",
            file_size=0,
            download_time=time.time() - start_time,
            error_message="Unknown error occurred",
        )

    async def download_all_chapters(
        self,
        chapters: list[HKEXChapter],
        output_dir: str,
        company_name: str,
        document_id: str,
        stock_code: str = "",
    ) -> BatchResult:
        """Download all chapters with progress display.

        Args:
            chapters: List of chapters to download
            output_dir: Output directory path
            company_name: Company name for file naming
            document_id: Document ID for file naming
            stock_code: Stock code for file naming

        Returns:
            BatchResult with overall download statistics
        """
        if not chapters:
            return BatchResult(
                total_chapters=0,
                successful_downloads=0,
                failed_downloads=0,
                download_results=[],
                total_size=0,
                total_time=0.0,
                errors=[],
            )

        start_time = time.time()

        # Create progress display
        with Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            "•",
            TextColumn("{task.completed}/{task.total} files"),
            "•",
            TimeRemainingColumn(),
            console=self.console,
        ) as progress:

            task = progress.add_task(
                f"Downloading {len(chapters)} chapters...",
                total=len(chapters)
            )

            # Create semaphore for concurrent control
            semaphore = asyncio.Semaphore(self.max_concurrent)

            async def download_with_semaphore(chapter: HKEXChapter) -> DownloadResult:
                async with semaphore:
                    # Add random delay between requests (1-3 seconds)
                    await asyncio.sleep(random.uniform(1, 3))

                    result = await self.download_chapter(
                        chapter, output_dir, company_name, document_id, stock_code
                    )

                    progress.advance(task)
                    return result

            # Execute downloads concurrently
            tasks = [download_with_semaphore(chapter) for chapter in chapters]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        download_results = []
        errors = []
        successful_downloads = 0
        total_size = 0

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_msg = f"Chapter {chapters[i].chapter_number}: {result!s}"
                errors.append(error_msg)
                download_results.append(
                    DownloadResult(
                        success=False,
                        pdf_path="",
                        metadata_path="",
                        file_size=0,
                        download_time=0.0,
                        error_message=error_msg,
                    )
                )
            elif isinstance(result, DownloadResult):
                download_results.append(result)
                if result.success:
                    successful_downloads += 1
                    total_size += result.file_size
                elif result.error_message:
                    errors.append(result.error_message)

        total_time = time.time() - start_time
        failed_downloads = len(chapters) - successful_downloads

        return BatchResult(
            total_chapters=len(chapters),
            successful_downloads=successful_downloads,
            failed_downloads=failed_downloads,
            download_results=download_results,
            total_size=total_size,
            total_time=total_time,
            errors=errors,
        )

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem compatibility.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename safe for filesystem use
        """
        import unicodedata

        # Normalize unicode characters to handle different encodings
        sanitized = unicodedata.normalize("NFC", filename)

        # Replace only filesystem-problematic characters, keep Unicode characters (including Chinese)
        replacements = {
            "/": "_",
            "\\": "_",
            ":": "_",
            "*": "_",
            "?": "_",
            '"': "_",
            "<": "_",
            ">": "_",
            "|": "_",
            "\n": "_",
            "\r": "_",
            "\t": "_",
        }

        for old, new in replacements.items():
            sanitized = sanitized.replace(old, new)

        # Remove extra spaces and limit length (be careful with Unicode character length)
        sanitized = " ".join(sanitized.split())

        # Limit length by character count, not byte count
        if len(sanitized) > 100:
            sanitized = sanitized[:100]

        # If the filename is empty after sanitization, use a default
        if not sanitized.strip():
            sanitized = "chapter"

        return sanitized.strip()

    def _generate_english_company_name(self, chinese_name: str) -> str:
        """Generate English company name from Chinese name.

        Args:
            chinese_name: Original Chinese company name

        Returns:
            English company name suitable for filesystem
        """
        # Common company name patterns and mappings
        name_mappings = {
            "有限公司": "Limited",
            "股份有限公司": "Co_Ltd",
            "控股": "Holdings",
            "集团": "Group",
            "国际": "International",
            "投资": "Investment",
            "发展": "Development",
            "科技": "Technology",
            "金融": "Finance",
            "银行": "Bank",
            "保险": "Insurance",
            "地产": "Real_Estate",
            "建设": "Construction",
            "工程": "Engineering",
            "制造": "Manufacturing",
            "贸易": "Trading",
            "服务": "Services",
            "医疗": "Medical",
            "教育": "Education",
            "能源": "Energy",
            "电力": "Power",
            "通信": "Communications",
            "传媒": "Media",
            "娱乐": "Entertainment",
            "餐饮": "Catering",
            "零售": "Retail",
            "物流": "Logistics",
            "运输": "Transportation"
        }

        # Start with the original name
        english_name = chinese_name

        # Apply mappings
        for chinese, english in name_mappings.items():
            english_name = english_name.replace(chinese, english)

        # Clean up the name - keep only ASCII characters for filesystem compatibility
        import re
        # Replace non-ASCII characters with underscores (including Chinese characters)
        english_name = re.sub(r"[^\x00-\x7F]", "_", english_name)  # Remove non-ASCII
        # Replace any remaining problematic characters with underscores
        english_name = re.sub(r"[^\w\s]", "_", english_name)
        # Replace spaces with underscores
        english_name = re.sub(r"\s+", "_", english_name)
        # Collapse multiple underscores
        english_name = re.sub(r"_+", "_", english_name)
        # Remove leading/trailing underscores
        english_name = english_name.strip("_")

        # If empty after processing, use generic name
        if not english_name:
            english_name = "Company"

        # Limit length
        if len(english_name) > 50:
            english_name = english_name[:50]

        return english_name
