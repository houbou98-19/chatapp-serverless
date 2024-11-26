from pydantic import BaseModel # type: ignore

class Message(BaseModel):
    content: str
