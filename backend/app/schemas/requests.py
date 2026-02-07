from typing import Literal

from pydantic import BaseModel, Field


class FTSFilterOption(BaseModel):
    column: str
    values: list[str] | str


class FullTextSearchRequest(BaseModel):
    search_string: str | None = None
    filters: list[FTSFilterOption] | None = None
    page: int = Field(1, ge=1, description="Page number, must be >= 1")
    page_size: int = Field(50, ge=1, le=100, description="Number of results per page")
    sort_by_date: bool | None = Field(False, description="Sort results by date descending if True.")
    response_type: Literal["parsed", "raw", "both"] | None = Field(
        "parsed",
        description="Select 'parsed' (default), 'raw', or 'both' for response data.",
    )
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "search_string": "",
                    "filters": [
                        {"column": "tables", "values": ["Answers", "Court Decisions"]},
                        {
                            "column": "jurisdictions",
                            "values": ["Switzerland", "France"],
                        },
                        {
                            "column": "Themes",
                            "values": ["Party autonomy", "Freedom of choice"],
                        },
                    ],
                    "page": 1,
                    "page_size": 100,
                    "sort_by_date": True,
                    "response_type": "parsed",
                },
            ]
        }
    }


class CuratedDetailsRequest(BaseModel):
    table: str
    id: str
    response_type: Literal["parsed", "raw", "both"] | None = Field(
        "parsed",
        description="Select 'parsed' (default), 'raw', or 'both' for response data.",
    )
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "table": "Answers",
                    "id": "CHE_15-TC",
                    "response_type": "parsed",
                },
            ]
        }
    }


FilterValue = str | int | bool


class FTFilterOption(BaseModel):
    column: str
    value: FilterValue | list[FilterValue]


class FullTableRequest(BaseModel):
    table: str
    filters: list[FTFilterOption] | None = None
    response_type: Literal["parsed", "raw", "both"] | None = Field(
        "parsed",
        description="Select 'parsed' (default), 'raw', or 'both' for response data.",
    )
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "table": "Answers",
                    "filters": [{"column": "Jurisdictions", "value": "Switzerland"}],
                    "response_type": "parsed",
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
