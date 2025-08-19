import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    APP_NAME: str = "CoLD FastAPI Backend"
    API_VERSION: str = "1.0.0"
    JWT_SECRET: str = os.getenv("JWT_SECRET", "MYSECRET")
    SQL_CONN_STRING = os.getenv("SQL_CONN_STRING")
    MONGODB_CONN_STRING = os.getenv("MONGODB_CONN_STRING")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    IPINFO_ACCESS_TOKEN = os.getenv("IPINFO_ACCESS_TOKEN")
    TEST = os.getenv("TEST")
    # NocoDB configuration
    NOCODB_BASE_URL = os.getenv("NOCODB_BASE_URL")
    NOCODB_API_TOKEN = os.getenv("NOCODB_API_TOKEN")
    NOCODB_POSTGRES_SCHEMA = os.getenv("NOCODB_POSTGRES_SCHEMA")


config = Config()
