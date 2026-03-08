import json
from pathlib import Path

from app.main import app

schema = app.openapi()

PREFIX = "/api/v1"
schema["paths"] = {path[len(PREFIX) :]: value for path, value in schema["paths"].items() if path.startswith(PREFIX)}
schema["servers"] = [{"url": "/api/proxy"}]

output = Path(__file__).resolve().parent.parent.parent / "frontend" / "app" / "types" / "openapi.json"
output.write_text(json.dumps(schema, indent=2) + "\n")
print(f"OpenAPI schema exported to {output}")
