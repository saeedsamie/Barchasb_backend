from fastapi import APIRouter, HTTPException

from app.schemas.user import User
from app.services.user_service import create_user

router = APIRouter()

users_db = {}


@router.post("/signup")
def signup(user: User):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    users_db.update(create_user(user).dict())
    print(users_db)
    return {"message": f"User {user} created successfully"}


@router.post("/login")
def login(username: str, password: str):
    user = users_db.get(username)
    if not user or user.password != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful"}


@router.get("/me")
def get_user(username: str):
    user = users_db.get(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/logout")
def logout(username: str):
    if username not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    # Logic for invalidating session or token can go here
    return {"message": f"User {username} successfully logged out"}
