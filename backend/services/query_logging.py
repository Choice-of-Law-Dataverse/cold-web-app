import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
import requests

#uri = os.getenv('MONGODB_CONN_STRING')
uri = "mongodb+srv://simonweigold:aussicht45%3FINSELI@cold-query-logging.ltft2.mongodb.net/?retryWrites=true&w=majority&appName=cold-query-logging"
print(uri)

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['query_logs']
collection = db['queries']

# Function to extract IP address
def get_ip_address(request):
    if request.headers.get('X-Forwarded-For'):
        ip = request.headers['X-Forwarded-For'].split(',')[0]
    else:
        ip = request.remote_addr
    return ip

# Function to get location from IP address
def get_location(ip_address):
    try:
        response = requests.get(f'http://ipinfo.io/{ip_address}/json')
        return response.json()
    except requests.RequestException as e:
        print(f"Error getting location: {e}")
        return None

# Function to log the query and user information
def log_query(request, search_string, results_count):
    timestamp = datetime.utcnow()
    ip_address = get_ip_address(request)
    location = get_location(ip_address)
    user_agent = request.headers.get('User-Agent')

    log_data = {
        'timestamp': timestamp,
        'ip_address': ip_address,
        'location': location,
        'user_agent': user_agent,
        'search_string': search_string,
        'results_count': results_count
    }

    collection.insert_one(log_data)
    print("Logged query:", log_data)