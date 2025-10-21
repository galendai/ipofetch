"""HKEXnews specific downloader for chapter-based PDF downloads."""

import asyncio
import random
import time
from pathlib import Path
from typing import List
from typing import Optional

import httpx
from rich.console import Console
from rich.progress import BarColumn
from rich.progress import DownloadColumn
from rich.progress import Progress
from rich.progress import TaskID
from rich.progress import TextColumn
from rich.progress import TimeRemainingColumn
from rich.progress import TransferSpeedColumn

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
        self.console = Console()

    async def download_chapter(
        self,
        chapter: HKEXChapter,
        output_dir: str,
        company_name: str,
        document_id: str,
    ) -> DownloadResult:
        """Download a single chapter.

        Args:
            chapter: Chapter information
            output_dir: Output directory path
            company_name: Company name for file naming
            document_id: Document ID for file naming

        Returns:
            DownloadResult with download status and metadata
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate filename
        safe_company_name = self._sanitize_filename(company_name)
        safe_chapter_title = self._sanitize_filename(chapter.chapter_title)
        filename = f"{safe_company_name}_{document_id}_chapter_{chapter.chapter_number:02d}_{safe_chapter_title}.pdf"
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
                    timeout=self.timeout,
                    headers={"User-Agent": self.user_agent},
                ) as client:
                    response = await client.get(chapter.pdf_url)
                    response.raise_for_status()

                    # Write file
                    with open(file_path, "wb") as f:
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
                elif e.response.status_code == 429:
                    # Rate limited, wait longer
                    wait_time = 60 * (attempt + 1)
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    # Other HTTP errors, retry with exponential backoff
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                    continue

            except Exception as e:
                # Network or other errors, retry with exponential backoff
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
                if attempt == self.max_retries - 1:
                    return DownloadResult(
                        success=False,
                        pdf_path="",
                        metadata_path="",
                        file_size=0,
                        download_time=time.time() - start_time,
                        error_message=f"Failed after {self.max_retries} attempts: {str(e)}",
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
        chapters: List[HKEXChapter],
        output_dir: str,
        company_name: str,
        document_id: str,
    ) -> BatchResult:
        """Download all chapters with progress display.

        Args:
            chapters: List of chapters to download
            output_dir: Output directory path
            company_name: Company name for file naming
            document_id: Document ID for file naming

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
            DownloadColumn(),
            "•",
            TransferSpeedColumn(),
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
                        chapter, output_dir, company_name, document_id
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
                error_msg = f"Chapter {chapters[i].chapter_number}: {str(result)}"
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
                else:
                    if result.error_message:
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
        # Replace problematic characters
        replacements = {
            '/': '_',
            '\\': '_',
            ':': '_',
            '*': '_',
            '?': '_',
            '"': '_',
            '<': '_',
            '>': '_',
            '|': '_',
            '\n': '_',
            '\r': '_',
            '\t': '_',
        }
        
        sanitized = filename
        for old, new in replacements.items():
            sanitized = sanitized.replace(old, new)
        
        # Remove extra spaces and limit length
        sanitized = ' '.join(sanitized.split())
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        
        return sanitized.strip()