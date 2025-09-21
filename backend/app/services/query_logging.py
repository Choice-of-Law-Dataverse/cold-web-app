import logging
from collections.abc import Callable
from datetime import UTC, datetime

from fastapi import Request, Response
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from app.config import config

logger = logging.getLogger(__name__)

client = MongoClient(config.MONGODB_CONN_STRING, server_api=ServerApi("1"))
db = client["query_logs"]
collection = db["queries"]


async def log_query(request: Request, call_next: Callable) -> Response:
    body_bytes = await request.body()

    import json

    try:
        request_json = json.loads(body_bytes)
    except (json.JSONDecodeError, UnicodeDecodeError):
        request_json = None

    async def custom_receive():
        return {
            "type": "http.request",
            "body": body_bytes,
            "more_body": False,
        }

    # new_request = Request(request.scope, custom_receive)
    request._receive = custom_receive

    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("User-Agent", "unknown")
    client_hints = {k: v for k, v in request.headers.items() if k.lower().startswith("sec-ch")}
    hostname = request.url.hostname
    route = request.url.path

    log_data = {
        "timestamp": datetime.now(UTC),
        "ip_address": ip_address,
        "user_agent": user_agent,
        "client_hints": client_hints,
        "hostname": hostname,
        "route": route,
        "request_body": request_json,
    }

    collection.insert_one(log_data)
    print("Logged query:", log_data)

    response = await call_next(request)
    return response
