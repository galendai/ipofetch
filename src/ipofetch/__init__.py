"""IPO Prospectus Fetcher CLI Tool.

A lightweight Python CLI tool for downloading IPO prospectus PDFs from various exchanges.
Supports China (cninfo), Hong Kong (HKEXnews), and US (SEC EDGAR) exchanges.
"""

__version__ = "1.0.0"
__author__ = "IPOFetch Team"
__email__ = "team@ipofetch.com"
__description__ = "A lightweight Python CLI tool for downloading IPO prospectus PDFs"

# Public API exports
from ipofetch.core.api import download_prospectus_from_url


__all__ = [
    "__author__",
    "__description__",
    "__email__",
    "__version__",
    "download_prospectus_from_url",
]
