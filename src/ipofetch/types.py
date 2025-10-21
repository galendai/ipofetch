"""Type definitions for IPO Prospectus Fetcher."""

from enum import Enum
from typing import Any
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional


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
    error_message: Optional[str] = None


class ParseResult(NamedTuple):
    """Result of URL parsing operation."""

    pdf_links: List[str]
    exchange_type: ExchangeType
    company_name: Optional[str] = None
    document_title: Optional[str] = None


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
