import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    APP_NAME: str = "CoLD FastAPI Backend"
    API_VERSION: str = "1.0.0"
    JWT_SECRET: str = os.getenv("JWT_SECRET", "MYSECRET")
    SQL_CONN_STRING: str | None = os.getenv("SQL_CONN_STRING")
    MONGODB_CONN_STRING: str | None = os.getenv("MONGODB_CONN_STRING")
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    TEST: str | None = os.getenv("TEST")
    # NocoDB configuration
    NOCODB_BASE_URL: str | None = os.getenv("NOCODB_BASE_URL")
    NOCODB_API_TOKEN: str | None = os.getenv("NOCODB_API_TOKEN")
    NOCODB_POSTGRES_SCHEMA: str | None = os.getenv("NOCODB_POSTGRES_SCHEMA")
    # Suggestions storage configuration
    SUGGESTIONS_SQL_CONN_STRING: str | None = os.getenv("SUGGESTIONS_SQL_CONN_STRING")
    # Moderation UI credentials (basic form login)
    MODERATION_USERNAME: str | None = os.getenv("MODERATION_USERNAME")
    MODERATION_PASSWORD: str | None = os.getenv("MODERATION_PASSWORD")

    def __post_init__(self) -> None:
        # Set MODERATION_SECRET after initialization to use JWT_SECRET as fallback
        self.MODERATION_SECRET: str = os.getenv("MODERATION_SECRET", self.JWT_SECRET)


config = Config()
