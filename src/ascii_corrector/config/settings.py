"""Application settings following 12-factor app principles."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.

    All settings can be overridden via environment variables
    with the ASCII_CORR_ prefix.

    Example:
        ASCII_CORR_TOLERANCE=2
        ASCII_CORR_LOG_LEVEL=DEBUG
    """

    model_config = SettingsConfigDict(
        env_prefix="ASCII_CORR_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Detection settings
    tolerance: int = Field(
        default=1,
        ge=0,
        le=10,
        description="Row/column tolerance for parallel line detection",
    )
    min_line_length: int = Field(
        default=2,
        ge=1,
        description="Minimum characters to consider as a line",
    )
    min_overlap_ratio: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum overlap ratio to consider lines parallel",
    )

    # Correction settings
    preserve_connections: bool = Field(
        default=True,
        description="Adjust corners/junctions when shifting lines",
    )
    dry_run: bool = Field(
        default=False,
        description="Analyze without applying corrections",
    )

    # Logging settings
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)",
    )
    log_format: str = Field(
        default="json",
        description="Log output format (json, console)",
    )

    # I/O settings
    default_encoding: str = Field(
        default="utf-8",
        description="Default file encoding",
    )
