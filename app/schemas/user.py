from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str
    points: int = 0


class UserCreate(BaseModel):
    username: str
    password: str
