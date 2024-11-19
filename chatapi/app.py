import os
from fastapi import FastAPI, Depends, HTTPException, status, Response, Request # type: ignore
from fastapi.responses import FileResponse, JSONResponse # type: ignore
from fastapi.staticfiles import StaticFiles # type: ignore
from fastapi.security import OAuth2PasswordRequestForm # type: ignore
from fastapi.responses import RedirectResponse # type: ignore
from jose import JWTError, jwt # type: ignore
from datetime import datetime, timedelta # type: ignore
from pydantic import BaseModel # type: ignore
from pymongo import MongoClient # type: ignore
from dotenv import load_dotenv # type: ignore
from mangum import Mangum # type: ignore

# Load environment variables
load_dotenv(dotenv_path=".env")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
SECRET_KEY = os.getenv("SECRET_KEY")
mongodb_url = os.getenv("MONGODB_URL")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

class User(BaseModel):
    username: str

class Token(BaseModel):
    access_token: str
    token_type: str

class Message(BaseModel):
    username: str
    content: str

def connect_to_mongo():
    client = MongoClient(mongodb_url)
    return client

def get_collection():
    client = connect_to_mongo()
    db = client["Chats"]
    collection = db["messages"]
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
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    try:
        return verify_token(token)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

# Authentication and authorization endpoints
@app.post("/token")
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != "test" or form_data.password != "test":  # Replace with database user lookup
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    access_token = create_access_token(data={"sub": form_data.username})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,  # Set to True if using HTTPS
        samesite="Lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return {"message": "Login successful"}

@app.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logout successful"}

# Chat endpoints
@app.get("/messages")
async def get_messages(response: Response, current_user: User = Depends(get_current_user)):
    collection = get_collection()
    messages = list(collection.find({}, {"_id": 0, "username": 1, "messagecontent": 1}))
    return JSONResponse(content=messages)

@app.post("/messages")
async def post_message(message: Message, current_user: User = Depends(get_current_user)):
    collection = get_collection()
    collection.insert_one({"username": message.username, "messagecontent": message.content})
    return {"status": "Message posted successfully"}

@app.get("/chat")
async def read_chat(current_user: User = Depends(get_current_user)):
    if isinstance(current_user, RedirectResponse):
        return current_user
    return FileResponse(os.path.join("static", "chat.html"))

@app.get("/login")
async def login_page():
    return FileResponse(os.path.join("static", "login.html"))

handler = Mangum(app)

def lambda_handler(event, context):
    """ This handler is for AWS Lambda integration with FastAPI """
    return handler(event, context)
