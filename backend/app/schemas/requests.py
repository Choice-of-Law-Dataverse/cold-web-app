from pydantic import BaseModel
from typing import List, Optional


class FullTextSearchRequest(BaseModel):
    search_string: Optional[str] = None
    filters: Optional[List[str]] = None


class CuratedDetailsRequest(BaseModel):
    table: str
    id: str


class FullTableRequest(BaseModel):
    table: str
    filters: Optional[List[str]] = None


class ClassifyQueryRequest(BaseModel):
    query: str
