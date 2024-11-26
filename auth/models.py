from pydantic import BaseModel # type: ignore

class User(BaseModel):
    username: str