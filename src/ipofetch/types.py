"""Type definitions for IPO Prospectus Fetcher."""

from __future__ import annotations

from enum import Enum
from typing import Any
from typing import Dict
from typing import NamedTuple


class ExchangeType(Enum):
    """Supported exchange types."""

    CNINFO = "cninfo"
    HKEXNEWS = "hkexnews"
    SEC_EDGAR = "sec_edgar"
    UNKNOWN = "unknown"


class DownloadResult(NamedTuple):
    """Result of a PDF download operation."""

    success: bool
    pdf_path: str
    metadata_path: str
    file_size: int
    download_time: float
    error_message: str | None = None


class ParseResult(NamedTuple):
    """Result of URL parsing operation."""

    pdf_links: list[str]
    exchange_type: ExchangeType
    company_name: str | None = None
    document_title: str | None = None


class DownloadMetadata(NamedTuple):
    """Metadata for a downloaded file."""

    original_url: str
    pdf_url: str
    file_path: str
    file_hash: str
    download_time: str
    file_size: int
    exchange_type: str
    tool_version: str


# Type aliases for better readability
URLString = str
FilePath = str
HTMLContent = str
JSONDict = Dict[str, Any]


class HKEXChapter(NamedTuple):
    """港交所招股说明书章节信息."""

    chapter_number: int
    chapter_title: str
    chapter_title_original: str  # 原始中文标题
    pdf_url: str
    relative_path: str


class ChapterMetadata(NamedTuple):
    """章节级元数据."""

    document_id: str
    company_name: str
    company_name_original: str  # 原始中文公司名
    chapter_number: int
    chapter_title: str  # 英文文件名(用于文件系统)
    chapter_title_original: str  # 原始中文标题
    pdf_url: str
    local_path: str
    file_size: int
    download_time: str
    language: str


class DocumentMetadata(NamedTuple):
    """文档级元数据."""

    document_id: str
    company_name: str  # 英文文件名(用于文件系统)
    company_name_original: str  # 原始中文公司名
    original_url: str
    total_chapters: int
    download_date: str
    chapters: list[ChapterMetadata]
    language: str
    exchange_type: str


class BatchResult(NamedTuple):
    """批量下载结果."""

    total_chapters: int
    successful_downloads: int
    failed_downloads: int
    download_results: list[DownloadResult]
    total_size: int
    total_time: float
    errors: list[str]
