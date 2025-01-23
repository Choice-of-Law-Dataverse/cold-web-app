import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SQL_CONN_STRING = os.getenv("SQL_CONN_STRING_PLAYGROUND")
    MIXEDBREAD_API_KEY = os.getenv("MIXEDBREAD_API_KEY")
    TEST = os.getenv("TEST")
    MONGODB_CONN_STRING = os.getenv("MONGODB_CONN_STRING")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    IPINFO_ACCESS_TOKEN = os.getenv("IPINFO_ACCESS_TOKEN")
