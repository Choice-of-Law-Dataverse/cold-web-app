from pydantic import BaseModel
from typing import List, Optional, Union


class FilterOption(BaseModel):
    column: str
    values: Union[str, List[str]]


class FullTextSearchRequest(BaseModel):
    search_string: Optional[str] = None
    filters: Optional[List[FilterOption]] = None


class CuratedDetailsRequest(BaseModel):
    table: str
    id: str


class FullTableRequest(BaseModel):
    table: str
    filters: Optional[List[str]] = None


class ClassifyQueryRequest(BaseModel):
    query: str
