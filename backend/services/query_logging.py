import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = os.getenv('MONGODB_CONN_STRING')

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Function to insert a list of dictionaries into the "queries" collection
def insert_query_logs(data_list):
    try:
        # Combine all dictionaries into one
        combined_dict = {}
        for d in data_list:
            combined_dict.update(d)
        
        # Access the query_logs database and the queries collection
        db = client['query_logs']
        collection = db['queries']
        
        # Insert the combined dictionary as a new document in MongoDB
        result = collection.insert_one(combined_dict)
        print(f"Inserted document with _id: {result.inserted_id}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
data_list = [
    {"query": "submarine"},
    {"timestamp": "2024-09-11T10:00:00Z"},
    {"ip_address": "0.0.0.0"}
]

insert_query_logs(data_list)

# Function to fetch and print all documents in a collection
def fetch_all_data(database_name, collection_name):
    try:
        db = client[database_name]
        collection = db[collection_name]
        documents = collection.find()
        for doc in documents:
            print(doc)
    except Exception as e:
        print(f"An error occurred: {e}")

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

fetch_all_data("query_logs", "queries")