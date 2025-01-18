from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
import requests
from app.config import config

# Create a new client and connect to the server
client = MongoClient(config.MONGODB_CONN_STRING, server_api=ServerApi("1"))
db = client["query_logs"]
collection = db["queries"]


# Function to extract IP address
def get_ip_address(request):
    if request.headers.get("X-Forwarded-For"):
        ip = request.headers["X-Forwarded-For"].split(",")[0]
    else:
        ip = request.remote_addr
    return ip


# Function to get location from IP address
def get_location(ip_address):
    access_token = Config.IPINFO_ACCESS_TOKEN
    try:
        response = requests.get(
            f"http://ipinfo.io/{ip_address}/json?token={access_token}"
        )
        return response.json()
    except requests.RequestException as e:
        print(f"Error getting location: {e}")
        return None


# Function to extract Client Hints
def get_client_hints(request):
    return {
        "brand": request.headers.get("Sec-CH-UA", "Unknown"),
        "mobile": request.headers.get("Sec-CH-UA-Mobile", "Unknown"),
        "platform": request.headers.get("Sec-CH-UA-Platform", "Unknown Platform"),
        "platform_version": request.headers.get(
            "Sec-CH-UA-Platform-Version", "Unknown Version"
        ),
        "model": request.headers.get("Sec-CH-UA-Model", "Unknown Model"),
    }


# Function to log the query and user information
def log_query(request, search_string, filters, results_count, route):
    timestamp = datetime.utcnow()
    ip_address = get_ip_address(request)
    location = get_location(ip_address)
    user_agent = request.headers.get("User-Agent")
    client_hints = get_client_hints(request)

    # Extract hostname from the JSON payload
    data = request.json
    hostname = data.get("hostname", "Unknown")  # Default to 'Unknown' if not provided

    log_data = {
        "timestamp": timestamp,
        "ip_address": ip_address,
        "location": location,
        "user_agent": user_agent,
        "client_hints": client_hints,
        "search_string": search_string,
        "filters": filters,
        "results_count": results_count,
        "route": route,
        "hostname": hostname,
    }

    collection.insert_one(log_data)
    print("Logged query:", log_data)
