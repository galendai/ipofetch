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
- 📝 **Metadata Generation**: Creates JSON metadata for each downloaded file with original Chinese names preserved
- 🌏 **Filename Localization**: Uses English filenames to avoid encoding issues while preserving original names in metadata
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

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run code formatting
ruff format

# Run linting and fix auto-fixable issues
ruff check --fix

# Run all checks (including security, complexity, etc.)
ruff check

# Run type checking
mypy src/

# Run tests with coverage
pytest --cov=ipofetch --cov-report=html
```

### Code Quality Tools

This project uses several tools to maintain high code quality:

- **[Ruff](https://docs.astral.sh/ruff/)**: Ultra-fast Python linter and formatter
  - Replaces multiple tools: flake8, isort, black, and more
  - Configured in `ruff.toml` with comprehensive rule sets
  - Enforces PEP 8, security best practices, and code complexity limits

- **[MyPy](https://mypy.readthedocs.io/)**: Static type checker
  - Ensures type safety with strict configuration
  - All functions must have proper type annotations

- **[Pytest](https://pytest.org/)**: Testing framework
  - Includes coverage reporting
  - Configured for unit and integration tests

#### Code Quality Standards

- **Line Length**: 88 characters (Black-compatible)
- **Python Version**: 3.8+ compatibility required
- **Type Hints**: Mandatory for all public functions and methods
- **Docstrings**: Google-style docstrings for public APIs
- **Import Style**: Single-line imports, sorted alphabetically
- **Security**: Bandit security checks enabled
- **Complexity**: McCabe complexity limit of 10

### Project Structure

```
src/ipofetch/
├── __init__.py          # Package initialization and public API
├── __main__.py          # Module entry point for python -m ipofetch
├── main.py              # CLI entry point with Typer
├── types.py             # Type definitions and data models
├── core/                # Core business logic
│   ├── __init__.py
│   ├── api.py           # Main API functions
│   └── hkex_api.py      # Hong Kong Exchange specific API
├── parsers/             # URL parsers for different exchanges
│   ├── __init__.py
│   ├── base.py          # Base parser interface
│   ├── cninfo.py        # China (cninfo) parser
│   ├── hkexnews.py      # Hong Kong Exchange parser
│   └── sec_edgar.py     # US SEC EDGAR parser
├── downloader/          # PDF download functionality
│   ├── __init__.py
│   ├── pdf_downloader.py    # Generic PDF downloader
│   └── hkex_downloader.py   # Hong Kong Exchange specific downloader
├── metadata/            # Metadata generation and management
│   ├── __init__.py
│   ├── generator.py         # Generic metadata generator
│   └── hkex_generator.py    # Hong Kong Exchange metadata generator
└── config/              # Configuration management
    ├── __init__.py
    └── settings.py      # Application settings and environment variables
```

#### Key Components

- **CLI Interface** (`main.py`): Built with Typer for type-safe command-line interface
- **Core APIs** (`core/`): Business logic separated by exchange type
- **Parsers** (`parsers/`): Extract PDF URLs from different exchange websites
- **Downloaders** (`downloader/`): Handle PDF downloads with retry logic and progress tracking
- **Metadata** (`metadata/`): Generate structured metadata for downloaded files
- **Configuration** (`config/`): Centralized settings management with Pydantic

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please use the [GitHub Issues](https://github.com/ipofetch/ipofetch/issues) page.