from fastapi import APIRouter, Depends, HTTPException, Response, status # type: ignore
from fastapi.responses import FileResponse # type: ignore
from fastapi.security import OAuth2PasswordRequestForm # type: ignore
from auth.utils import create_access_token, verify_password, hash_password # type: ignore
from database.connection import get_collection # type: ignore
import os

router = APIRouter()

@router.post("/register")
async def register_user(form_data: OAuth2PasswordRequestForm = Depends()):
    collection = get_collection("users")
    if collection.find_one({"username": form_data.username}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    hashed_password = hash_password(form_data.password)
    collection.insert_one({"username": form_data.username, "password": hashed_password})

    return {"message": "User registered successfully"}

@router.post("/token")
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
        samesite="Lax"
    )
    return {"message": "Login successful"}

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logout successful"}


@router.get("/login")
async def read_login_page():
    return FileResponse(os.path.join("static", "login.html"))
