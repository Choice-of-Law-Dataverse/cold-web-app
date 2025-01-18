import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    APP_NAME: str = "CoLD FastAPI Backend"
    API_VERSION: str = "1.0.0"
    API_KEY: str = os.getenv("API_KEY", "mysecretkey")
    SQL_CONN_STRING = os.getenv("SQL_CONN_STRING")
    MONGODB_CONN_STRING = os.getenv("MONGODB_CONN_STRING")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    IPINFO_ACCESS_TOKEN = os.getenv("IPINFO_ACCESS_TOKEN")
    TEST = os.getenv("TEST")


config = Config()
