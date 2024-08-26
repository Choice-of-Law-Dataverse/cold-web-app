import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    AZURE_POSTGRESQL_DUMMY_CONN_STRING = os.getenv("AZURE_POSTGRESQL_DUMMY_CONN_STRING")
    AZURE_SQL_CONNECTION_STRING = os.getenv("AZURE_SQL_CONNECTION_STRING")
    MIXEDBREAD_API_KEY = os.getenv("MIXEDBREAD_API_KEY")
    TEST = os.getenv("TEST")
