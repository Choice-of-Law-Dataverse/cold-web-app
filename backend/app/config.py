import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    SQL_CONN_STRING: str | None = os.getenv("SQL_CONN_STRING")
    MONGODB_CONN_STRING: str | None = os.getenv("MONGODB_CONN_STRING")
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    TEST: str | None = os.getenv("TEST")
    # Logging configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    # NocoDB configuration
    NOCODB_BASE_URL: str | None = os.getenv("NOCODB_BASE_URL")
    NOCODB_API_TOKEN: str | None = os.getenv("NOCODB_API_TOKEN")
    NOCODB_POSTGRES_SCHEMA: str | None = os.getenv("NOCODB_POSTGRES_SCHEMA")
    # Suggestions storage configuration
    SUGGESTIONS_SQL_CONN_STRING: str | None = os.getenv("SUGGESTIONS_SQL_CONN_STRING")
    # Moderation UI credentials (basic form login)
    MODERATION_USERNAME: str | None = os.getenv("MODERATION_USERNAME")
    MODERATION_PASSWORD: str | None = os.getenv("MODERATION_PASSWORD")
    MODERATION_SECRET: str = os.getenv("MODERATION_SECRET", os.getenv("API_KEY", "secret"))
    # Auth0 configuration
    AUTH0_DOMAIN: str | None = os.getenv("AUTH0_DOMAIN")
    AUTH0_AUDIENCE: str | None = os.getenv("AUTH0_AUDIENCE")
    # Frontend API key for request validation
    API_KEY: str | None = os.getenv("API_KEY")


config = Config()
