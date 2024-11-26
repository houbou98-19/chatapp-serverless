from pymongo import MongoClient
import os

mongodb_url = os.getenv("MONGODB_URL")

def connect_to_mongo():
    client = MongoClient(mongodb_url)
    return client

def get_collection(collection_name: str):
    client = connect_to_mongo()
    db = client["Chats"]
    return db[collection_name]
