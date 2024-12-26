from fastapi import APIRouter, HTTPException
from starlette import status

from app.schemas.user import User, UserCreate
from app.services.user_service import verify_password, create_user

router = APIRouter()

users_db = dict()


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate):
    if user.username in users_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Username already exists')
    new_user = create_user(user)
    users_db.update({new_user.username: {'password': new_user.password, 'points': 0}})
    return {"message": "User created successfully", "username": new_user.username}


@router.post("/login")
def login(user: User):
    user_data = users_db.get(user.username)
    if not user_data or not verify_password(user.password, user_data['password']):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
    return {"message": "Login successful", "username": user.username}


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
