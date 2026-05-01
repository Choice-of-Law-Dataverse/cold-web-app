from pydantic import BaseModel


class FTSFilterOption(BaseModel):
    column: str
    values: list[str] | str


FilterValue = str | int | bool


class FTFilterOption(BaseModel):
    column: str
    value: FilterValue | list[FilterValue]
