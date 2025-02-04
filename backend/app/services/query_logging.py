from datetime import datetime

from fastapi import Request
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from app.config import config
from app.services.utils import get_location
from app.schemas.logging import QueryLog


# Create a new client and connect to the server
client = MongoClient(config.MONGODB_CONN_STRING, server_api=ServerApi("1"))
db = client["query_logs"]
collection = db["queries"]


async def log_query(request: Request, call_next):
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("User-Agent", "unknown")
    client_hints = {k: v for k, v in request.headers.items() if k.lower().startswith("sec-ch")}
    hostname = request.url.hostname
    route = request.url.path

    location = get_location(ip_address)

    log_data = {
        "timestamp": datetime.utcnow(),
        "ip_address": ip_address,
        "location": location,
        "user_agent": user_agent,
        "client_hints": client_hints,
        "hostname": hostname,
        "route": route,
    }

    collection.insert_one(log_data)
    print("Logged query:", log_data)

    response = await call_next(request)
    return response