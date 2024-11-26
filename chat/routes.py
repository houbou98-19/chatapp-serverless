from fastapi import APIRouter, Depends, Response # type: ignore
from fastapi.responses import JSONResponse, FileResponse  # type: ignore
from auth.utils import get_current_user # type: ignore
from database.connection import get_collection  # type: ignore
from chat.models import Message # type: ignore
from auth.models import User # type: ignore
import os

router = APIRouter()

@router.get("/messages")
async def get_messages(response: Response, current_user: User = Depends(get_current_user)):
    collection = get_collection("messages")
    messages = list(collection.find({}, {"_id": 0, "username": 1, "messagecontent": 1}))
    return JSONResponse(content=messages)

@router.post("/messages")
async def post_message(message: Message, current_user: User = Depends(get_current_user)):
    collection = get_collection("messages")
    collection.insert_one({"username": current_user.username, "messagecontent": message.content})
    return {"status": "Message posted successfully"}

@router.get("/chat")
async def read_chat_page():
    return FileResponse(os.path.join("static", "chat.html"))