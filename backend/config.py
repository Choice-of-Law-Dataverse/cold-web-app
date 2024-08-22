import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    AZURE_SQL_CONNECTION_STRING = os.getenv("AZURE_SQL_CONNECTION_STRING")
    MIXEDBREAD_API_KEY = os.getenv("MIXEDBREAD_API_KEY")
