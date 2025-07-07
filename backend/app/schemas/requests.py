from typing import List, Optional, Union
from pydantic import BaseModel, Field


class FTSFilterOption(BaseModel):
    column: str
    values: Union[List[str], str]


class FullTextSearchRequest(BaseModel):
    search_string: Optional[str] = None
    filters: Optional[List[FTSFilterOption]] = None
    page: int = Field(1, ge=1, description="Page number, must be >= 1")
    page_size: int = Field(50, ge=1, le=100, description="Number of results per page")
    sort_by_date: Optional[bool] = Field(False, description="Sort results by date descending if True.")


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
