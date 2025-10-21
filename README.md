# IPO Prospectus Fetcher

A lightweight Python CLI tool for downloading IPO prospectus PDFs from various exchanges.

## Overview

IPO Prospectus Fetcher (`ipofetch`) is a command-line tool that automatically downloads PDF files from prospectus web pages. It supports three major exchanges:

- **China**: cninfo.com.cn (巨潮资讯网)
- **Hong Kong**: HKEXnews
- **United States**: SEC EDGAR

## Features

- 🚀 **Simple CLI Interface**: Easy-to-use command-line interface with Typer
- 🌐 **Multi-Exchange Support**: Works with China, Hong Kong, and US exchanges
- 📄 **Automatic PDF Detection**: Intelligently finds and downloads prospectus PDFs
- 📊 **Rich Output**: Beautiful terminal output with progress indicators
- 🔄 **Retry Mechanism**: Robust download with automatic retry on failures
- 📝 **Metadata Generation**: Creates JSON metadata for each downloaded file
- 🐍 **Python API**: Programmatic interface for integration with other systems

## Installation

```bash
# Install from source
git clone https://github.com/ipofetch/ipofetch.git
cd ipofetch
pip install -e .

# Or install from PyPI (when available)
pip install ipofetch
```

## Usage

### Command Line Interface

```bash
# Basic usage
ipofetch https://example.com/prospectus-page

# Specify output directory
ipofetch https://example.com/prospectus-page --output ./downloads/

# Enable verbose output
ipofetch https://example.com/prospectus-page --verbose

# Show help
ipofetch --help

# Show version
ipofetch --version
```

### Python API

```python
from ipofetch import download_prospectus_from_url

# Download prospectus PDF
result = download_prospectus_from_url(
    url="https://example.com/prospectus-page",
    output_dir="./prospectus/"
)

if result["success"]:
    print(f"Downloaded: {result['pdf_path']}")
    print(f"File size: {result['file_size']} bytes")
    print(f"Download time: {result['download_time']:.2f}s")
else:
    print("Download failed")
```

## Requirements

- Python 3.8+
- Dependencies are automatically installed via pip

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/ipofetch/ipofetch.git
cd ipofetch

# Install development dependencies
pip install -e ".[dev]"

# Run code formatting
ruff format

# Run linting
ruff check

# Run tests
pytest
```

### Project Structure

```
src/ipofetch/
├── __init__.py          # Package initialization and public API
├── main.py              # CLI entry point
├── types.py             # Type definitions
├── core/                # Core business logic
│   ├── __init__.py
│   └── api.py           # Main API functions
├── parsers/             # URL parsers for different exchanges
│   ├── __init__.py
│   ├── base.py          # Base parser interface
│   ├── cninfo.py        # China (cninfo) parser
│   ├── hkexnews.py      # Hong Kong parser
│   └── sec_edgar.py     # US SEC EDGAR parser
├── downloader/          # PDF download functionality
│   ├── __init__.py
│   └── pdf_downloader.py
├── metadata/            # Metadata generation
│   ├── __init__.py
│   └── generator.py
└── config/              # Configuration management
    ├── __init__.py
    └── settings.py
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please use the [GitHub Issues](https://github.com/ipofetch/ipofetch/issues) page.