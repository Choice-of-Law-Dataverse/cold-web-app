from pydantic import BaseModel
from typing import Union, Any

class QueryLog(BaseModel):
    search_string: str
    filters: Union[dict, list, str, None] = None
    results_count: int
    route: str
    hostname: str = "Unknown"
  