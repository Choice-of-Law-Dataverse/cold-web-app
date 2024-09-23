import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    AZURE_POSTGRESQL_DUMMY_CONN_STRING = os.getenv("AZURE_POSTGRESQL_DUMMY_CONN_STRING")
    AZURE_SQL_CONNECTION_STRING = os.getenv("AZURE_SQL_CONNECTION_STRING")
    SQL_CONN_STRING = os.getenv("SQL_CONN_STRING")
    MIXEDBREAD_API_KEY = os.getenv("MIXEDBREAD_API_KEY")
    TEST = os.getenv("TEST")
    MONGODB_CONN_STRING = os.getenv("MONGODB_CONN_STRING")
