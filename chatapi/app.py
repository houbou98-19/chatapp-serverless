import json
import os
from fastapi import FastAPI, HTTPException # type: ignore
from fastapi.responses import FileResponse, JSONResponse # type: ignore
from pydantic import BaseModel # type: ignore
from typing import List
from mangum import Mangum # type: ignore
from pymongo import MongoClient
from dotenv import load_dotenv # type: ignore

load_dotenv(dotenv_path='.env') 
mongodb_url = os.getenv('MONGODB_URL')

app = FastAPI()

class Message(BaseModel):
    username: str
    content: str  # Keep this consistent with your HTML and MongoDB insertion

def connect_to_mongo():
    mongo_uri = os.getenv("MONGODB_URL")
    client = MongoClient(mongo_uri)
    return client

def get_collection():
    client = connect_to_mongo()
    db = client['Chats']
    collection = db['messages']
    return collection

@app.post("/messages")
async def post_message(message: Message):
    try:
        collection = get_collection()
        # Insert the message as a dictionary, with consistent keys
        collection.insert_one({"username": message.username, "messagecontent": message.content})
        
        return {"status": "Message posted successfully"}
    except Exception as e:
        return {"status": "Error", "message": str(e)}

@app.get("/messages")
async def get_messages():
    try:
        collection = get_collection()
        messages = list(collection.find({}, {"_id": 0, "username": 1, "messagecontent": 1}))  # Ensure keys match
        return JSONResponse(content=messages)
    except Exception as e:
        return {"status": "Error", "message": str(e)}

@app.get("/test-connection")
async def test_connection():
    try:
        print("Attempting to connect to MongoDB...")
        client = connect_to_mongo()
        db = client['Chats']
        collection = db['messages']
        
        first_document = collection.find_one()
        print("Connection successful! First document in the collection:", first_document)

        return {"status": "Connection successful"}
    except Exception as e:
        print("Error connecting to MongoDB:", e)
        return {"status": "Connection failed", "error": str(e)}

@app.get("/chat")
async def read_chat():
    return FileResponse(os.path.join("static", "chat.html"))

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

handler = Mangum(app)

def lambda_handler(event, context):
    """ This handler is for AWS Lambda integration with FastAPI """
    return handler(event, context)