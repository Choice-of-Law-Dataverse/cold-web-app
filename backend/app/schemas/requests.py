from typing import List, Optional, Union
from pydantic import BaseModel

class FilterOption(BaseModel):
    column: str
    value: Union[str, int, float]

class FullTextSearchRequest(BaseModel):
    search_string: Optional[str] = None
    filters: Optional[List[FilterOption]] = None

class CuratedDetailsRequest(BaseModel):
    table: str
    id: str

class FullTableRequest(BaseModel):
    table: str
    filters: Optional[List[FilterOption]] = None

class ClassifyQueryRequest(BaseModel):
    query: str
