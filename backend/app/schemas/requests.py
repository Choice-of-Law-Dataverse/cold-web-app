from typing import List, Optional, Union
from pydantic import BaseModel


class FTSFilterOption(BaseModel):
    column: str
    values: Union[List[str], str]


class FullTextSearchRequest(BaseModel):
    search_string: Optional[str] = None
    filters: Optional[List[FTSFilterOption]] = None


class CuratedDetailsRequest(BaseModel):
    table: str
    id: str


FilterValue = Union[str, int, bool]


class FTFilterOption(BaseModel):
    column: str
    value: Union[FilterValue, List[FilterValue]]


class FullTableRequest(BaseModel):
    table: str
    filters: Optional[List[FTFilterOption]] = None


class ClassifyQueryRequest(BaseModel):
    query: str
