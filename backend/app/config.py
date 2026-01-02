from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Application settings using Pydantic Settings for automatic environment variable loading."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    SQL_CONN_STRING: str | None = None
    MONGODB_CONN_STRING: str | None = None
    OPENAI_API_KEY: str | None = None
    TEST: str | None = None
    # Logging configuration
    LOG_LEVEL: str = "INFO"
    # NocoDB configuration
    NOCODB_BASE_URL: str | None = None
    NOCODB_API_TOKEN: str | None = None
    NOCODB_POSTGRES_SCHEMA: str | None = None
    # Suggestions storage configuration
    SUGGESTIONS_SQL_CONN_STRING: str | None = None
    # Moderation UI credentials (basic form login)
    MODERATION_USERNAME: str | None = None
    MODERATION_PASSWORD: str | None = None
    MODERATION_SECRET: str | None = None
    # Auth0 configuration
    AUTH0_DOMAIN: str | None = None
    AUTH0_AUDIENCE: str | None = None
    # Frontend API key for request validation
    API_KEY: str | None = None

    @model_validator(mode="after")
    def set_moderation_secret_fallback(self) -> "Config":
        """Set MODERATION_SECRET to API_KEY if not explicitly provided, fallback to 'secret'."""
        if self.MODERATION_SECRET is None:
            self.MODERATION_SECRET = self.API_KEY or "secret"
        return self


config = Config()
