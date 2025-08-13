from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings, loaded from environment variables or a .env file.

    This class defines the configuration parameters required for the application
    to run, including API keys, URLs, and other operational settings.
    """

    alert_api_key: str = Field(
        default="your_api_key",
        description="API key for Prewave alert services.",
        alias="ALERT_API_KEY",
    )
    alert_terms_api_url: str = Field(
        default="https://services.prewave.ai/adminInterface/api/testQueryTerm",
        description="URL for the alert terms API endpoint.",
        alias="ALERT_TERMS_API_URL",
    )
    alert_text_api_url: str = Field(
        default="https://services.prewave.ai/adminInterface/api/testAlerts",
        description="URL for the alert text API endpoint.",
        alias="ALERT_TEXT_API_URL",
    )
    host_port: int = Field(
        default=8000,
        description="Host port for running the application.",
        alias="HOST_PORT",
    )
    guest_port: int = Field(
        default=8000,
        description="Guest port for Docker container mapping.",
        alias="GUEST_PORT",
    )
    filter_by_language: bool = Field(
        default=True,
        description="Filter alert content by language before matching terms.",
        alias="FILTER_BY_LANGUAGE",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Instantiate the settings object for use throughout the application
settings = Settings()  # type: ignore
