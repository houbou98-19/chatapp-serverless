from fastapi import FastAPI # type: ignore
from fastapi.staticfiles import StaticFiles # type: ignore
from mangum import Mangum   # type: ignore
from auth.routes import router as auth_router   # type: ignore
from chat.routes import router as chat_router   # type: ignore
from database.connection import connect_to_mongo    # type: ignore

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth_router)
app.include_router(chat_router)

handler = Mangum(app)

# Lambda handler
def lambda_handler(event, context):
    return handler(event, context)
