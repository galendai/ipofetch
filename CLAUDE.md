# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

IPOFetch is a Python CLI tool for downloading IPO prospectus PDFs from multiple stock exchanges. It currently supports Hong Kong (HKEXnews), China (cninfo), and US (SEC EDGAR) exchanges. The tool features a rich CLI interface, automatic PDF detection, retry mechanisms, and metadata generation with localization support.

## Claude Code Interaction Rules

### Communication Standards
- **Language**: Always respond in Chinese (中文) when interacting with users
- **Documentation**: All code comments and documentation must be written in English
- **Code Cleanliness**: Clean up test scripts and test-generated files after running tests to maintain source code cleanliness

### Package Management
- **Use UV**: Always use `uv` for package management instead of pip
- **Environment Setup**: Use `uv venv` to create virtual environments
- **Dependency Management**: Use `uv add` and `uv remove` for dependencies
- **Development Tools**: Install dev dependencies with `uv add --dev`

## Development Commands

### Environment Setup
```bash
# Create virtual environment with uv
uv venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
uv pip install -e ".[dev]"

# Alternative: Add dependencies directly
uv add --dev ruff pytest pytest-cov mypy types-lxml
```

### Code Quality
```bash
# Format code
ruff format

# Lint and fix auto-fixable issues
ruff check --fix

# Run full linting (including security, complexity, etc.)
ruff check

# Type checking
mypy src/

# Run tests with coverage
pytest

# Run tests with coverage report
pytest --cov=ipofetch --cov-report=html --cov-report=term-missing

# Run specific test file
pytest tests/test_specific_file.py

# Run tests without slow ones
pytest -m "not slow"

# Clean up test artifacts after testing
rm -rf .pytest_cache/
rm -rf htmlcov/
rm -f .coverage
rm -f coverage.xml
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
```

### Building and Distribution
```bash
# Build package
python -m build

# Install from source in development mode using uv
uv pip install -e .
```

## Architecture Overview

### Core Components

**CLI Layer** (`main.py`): Built with Typer, provides rich terminal output with progress indicators and error handling.

**Core API** (`core/api.py`): Main public API entry point that routes to appropriate exchange-specific handlers. Currently supports HKEXnews with plans for other exchanges.

**Exchange-Specific APIs** (`core/hkex_api.py`): Specialized handlers for different exchanges. HKEX has dedicated API due to its complex chapter-based PDF structure.

**Parser System** (`parsers/`): Abstract base class `BaseParser` with exchange-specific implementations:
- `hkexnews.py`: Handles Hong Kong Exchange's complex multi-chapter prospectus structure
- `cninfo.py`: For China's cninfo.com.cn exchange
- `sec_edgar.py`: For US SEC EDGAR system

**Downloader System** (`downloader/`):
- `pdf_downloader.py`: Generic PDF download with retry logic and progress tracking
- `hkex_downloader.py`: Specialized for HKEX's chapter-based downloads with atomic file operations

**Metadata System** (`metadata/`):
- `generator.py`: Creates JSON metadata for downloaded files with hash verification
- `hkex_generator.py`: Handles complex HKEX chapter mapping and bilingual metadata

**Utilities** (`utils/`):
- `pdf_mapping.py`: Generates PDF chapter mapping files for navigation

### Type System

Uses comprehensive type definitions in `types.py`:
- `ExchangeType`: Enum for supported exchanges
- `DownloadResult`: NamedTuple for download operation results
- `ParseResult`: NamedTuple for URL parsing results
- `HKEXChapter`: Hong Kong Exchange-specific chapter information
- Various metadata NamedTuples for different levels of granularity

### Configuration

Settings managed via Pydantic in `config/settings.py` with environment variable support.

## Key Implementation Details

### HKEX Special Handling
HKEX prospectuses are divided into chapters that must be downloaded individually. The system:
1. Parses chapter listing from the main page
2. Downloads each chapter PDF atomically
3. Generates both chapter-level and document-level metadata
4. Creates PDF mapping files for navigation
5. Uses English filenames to avoid encoding issues while preserving Chinese names in metadata

### Error Handling
- Comprehensive exception handling with rich error messages
- Atomic file operations to prevent corruption
- Retry mechanisms for network failures
- Graceful degradation for unsupported URLs

### Testing Strategy
- Tests are currently minimal (empty tests directory)
- Pytest configured for unit and integration tests with coverage
- Markers for `slow`, `integration`, and `unit` tests
- Coverage reports generated in HTML and XML formats

## Development Standards

### Code Quality
- **Line Length**: 88 characters (Ruff default)
- **Python Version**: 3.8+ compatibility required
- **Type Hints**: Strict type checking with MyPy enabled
- **Docstrings**: Google-style convention (pydocstyle) - Must be in English
- **Security**: Bandit rules enabled via Ruff
- **Complexity**: McCabe limit of 10
- **Comments**: All code comments must be written in English
- **Language**: User interactions and responses must be in Chinese

### Import Organization
- Single-line imports enforced
- First-party imports (`ipofetch`) grouped separately
- Sorting and formatting handled by Ruff

### Error Handling Patterns
- Use specific exception types with descriptive messages
- Implement proper context managers for file operations
- Include retry logic for network operations
- Provide meaningful error messages to users

## File Structure Conventions

```
src/ipofetch/
├── __init__.py          # Public API exports
├── main.py              # CLI entry point
├── types.py             # All type definitions
├── core/                # Business logic
├── parsers/             # Exchange-specific parsers
├── downloader/          # File download logic
├── metadata/            # Metadata generation
├── config/              # Configuration management
└── utils/               # Utility functions
```

## Common Development Patterns

When adding new exchange support:
1. Create parser class inheriting from `BaseParser`
2. Implement `extract_pdf_links()` and `is_supported_url()` methods
3. Add exchange-specific downloader if needed
4. Create corresponding metadata generator
5. Add `ExchangeType` enum value
6. Update main API to route to new handler
7. Add comprehensive tests

When modifying existing functionality:
1. Maintain backward compatibility in public API
2. Update type definitions accordingly
3. Ensure error handling remains consistent
4. Run full test suite and coverage checks
5. Clean up all test artifacts and temporary files after testing
6. Update documentation as needed