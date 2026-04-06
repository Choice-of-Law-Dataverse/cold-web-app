import json
from pathlib import Path
from typing import Any

from app.main import app

schema = app.openapi()

PREFIX = "/api/v1"
schema["paths"] = {path[len(PREFIX) :]: value for path, value in schema["paths"].items() if path.startswith(PREFIX)}
schema["servers"] = [{"url": "/api/proxy"}]


def strip_field_titles(obj: Any) -> Any:
    if isinstance(obj, dict):
        if "properties" in obj:
            for prop in obj["properties"].values():
                if isinstance(prop, dict) and "title" in prop:
                    del prop["title"]
        return {k: strip_field_titles(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [strip_field_titles(item) for item in obj]
    return obj


schema["components"]["schemas"] = strip_field_titles(schema["components"]["schemas"])

output = Path(__file__).resolve().parent.parent.parent / "frontend" / "app" / "types" / "openapi.json"
output.write_text(json.dumps(schema, indent=2) + "\n")
print(f"OpenAPI schema exported to {output}")
