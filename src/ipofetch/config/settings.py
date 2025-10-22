"""Configuration settings for IPO Prospectus Fetcher."""
from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field
from pydantic_settings import BaseSettings


class ExchangeConfig(BaseModel):
    """Configuration for a specific exchange."""

    base_url: str = Field(..., description="Base URL of the exchange")
    pdf_selectors: list[str] = Field(
        default_factory=list, description="CSS selectors for PDF links"
    )
    keywords: list[str] = Field(
        default_factory=list, description="Keywords to identify prospectus documents"
    )


class AppSettings(BaseSettings):
    """Application settings with environment variable support."""

    # HTTP client settings
    user_agent: str = Field(
        default="IPOFetch/1.0.0",
        description="User agent string for HTTP requests",
    )
    request_timeout: int = Field(
        default=30, description="HTTP request timeout in seconds"
    )
    retry_attempts: int = Field(default=3, description="Number of retry attempts")
    retry_delay: float = Field(
        default=1.0, description="Delay between retries in seconds"
    )

    # File handling settings
    output_directory: str = Field(
        default="./prospectus/", description="Default output directory"
    )
    max_file_size: int = Field(
        default=100 * 1024 * 1024, description="Maximum file size in bytes (100MB)"
    )

    # Logging settings
    verbose: bool = Field(default=False, description="Enable verbose logging")
    log_level: str = Field(default="INFO", description="Logging level")

    # Exchange configurations
    exchanges: dict[str, ExchangeConfig] = Field(
        default_factory=lambda: {
            "cninfo": ExchangeConfig(
                base_url="http://www.cninfo.com.cn",
                pdf_selectors=["a[href$='.pdf']"],
                keywords=["招股说明书", "prospectus"],
            ),
            "hkexnews": ExchangeConfig(
                base_url="https://www1.hkexnews.hk",
                pdf_selectors=["a[href*='.pdf']"],
                keywords=["prospectus", "招股章程"],
            ),
            "sec_edgar": ExchangeConfig(
                base_url="https://www.sec.gov",
                pdf_selectors=["a[href*='.htm']"],
                keywords=["prospectus", "S-1", "F-1"],
            ),
        }
    )

    class Config:
        """Pydantic configuration."""

        env_prefix = "IPOFETCH_"
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = AppSettings()
