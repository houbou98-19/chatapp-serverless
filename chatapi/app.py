import os
from fastapi import FastAPI, Depends, HTTPException, status, Response, Request # type: ignore
from fastapi.responses import FileResponse, JSONResponse # type: ignore
from fastapi.staticfiles import StaticFiles # type: ignore
from fastapi.security import OAuth2PasswordRequestForm # type: ignore
from jose import JWTError, jwt # type: ignore
from datetime import datetime, timedelta # type: ignore
from pydantic import BaseModel # type: ignore
from pymongo import MongoClient # type: ignore
from dotenv import load_dotenv # type: ignore
from mangum import Mangum # type: ignore
import bcrypt # type: ignore

# Load environment variables
load_dotenv(dotenv_path=".env")

# Environment variables
SECRET_KEY = os.getenv("SECRET_KEY")
mongodb_url = os.getenv("MONGODB_URL")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

class User(BaseModel):
    username: str

class Message(BaseModel):
    content: str

def connect_to_mongo():
    client = MongoClient(mongodb_url)
    return client

def get_collection(collection):
    client = connect_to_mongo()
    db = client["Chats"]
    collection = db[collection]
    return collection

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return User(username=username)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
  
async def get_current_user(request: Request):  # Checks if user is authenticated and returns user object
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return verify_token(token)

# Utility function to hashed passwords
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8')) # return True if password matches

# Register and login endpoints
@app.post("/register")
async def register_user(form_data: OAuth2PasswordRequestForm = Depends()):
    collection = get_collection("users")
    if collection.find_one({"username": form_data.username}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    hashed_password = hash_password(form_data.password)
    collection.insert_one({"username": form_data.username, "password": hashed_password})

    return {"message": "User registered successfully"}

@app.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logout successful"}

# Authentication and authorization endpoints
@app.post("/token")
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    collection = get_collection("users")
    user = collection.find_one({"username": form_data.username})

    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": form_data.username})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return {"message": "Login successful"}

# Chat endpoints
@app.get("/messages")
async def get_messages(response: Response, current_user: User = Depends(get_current_user)):
    collection = get_collection("messages")
    messages = list(collection.find({}, {"_id": 0, "username": 1, "messagecontent": 1}))
    return JSONResponse(content=messages)

@app.post("/messages")
async def post_message(message: Message, current_user: User = Depends(get_current_user)):
    collection = get_collection("messages")
    collection.insert_one({"username": current_user.username, "messagecontent": message.content})
    return {"status": "Message posted successfully"}

# Page Serving Endpoints
@app.get("/chat")
async def read_chat(current_user: User = Depends(get_current_user)):
    return FileResponse(os.path.join("static", "chat.html"))

@app.get("/login")
async def login_page():
    return FileResponse(os.path.join("static", "login.html"))

handler = Mangum(app)

def lambda_handler(event, context):
    """ This handler is for AWS Lambda integration with FastAPI """
    return handler(event, context)
