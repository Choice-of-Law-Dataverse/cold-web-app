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
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "search_string": "",
                    "filters": [{"column": "tables", "values": ["Answers", "Court Decisions"]}, {"column": "jurisdictions", "values": ["Switzerland", "France"]}, {"column": "Themes", "values": ["Party autonomy", "Freedom of choice"]}],
                    "page": 1,
                    "page_size": 100,
                    "sort_by_date": True,
                },
            ]
        }
    }


class CuratedDetailsRequest(BaseModel):
    table: str
    id: str
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "table": "Answers",
                    "id": "CHE_15-TC"
                },
            ]
        }
    }


FilterValue = Union[str, int, bool]


class FTFilterOption(BaseModel):
    column: str
    value: Union[FilterValue, List[FilterValue]]


class FullTableRequest(BaseModel):
    table: str
    filters: Optional[List[FTFilterOption]] = None
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "table": "Answers",
                    "filters": [{"column": "Jurisdictions", "value": "Switzerland"}]
                },
            ]
        }
    }


class ClassifyQueryRequest(BaseModel):
    query: str
    model_config = {
        "json_schema_extra": {
            "examples": [
                {"query": "How do courts treat party autonomy?"},
            ]
        }
    }
