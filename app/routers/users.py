from fastapi import APIRouter, HTTPException
from starlette import status

from app.schemas.user import User, UserCreate
from app.services.user_service import verify_password

router = APIRouter()

users_db = dict()


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate):
    if user.username in users_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Username already exists')
    users_db.update({user.username: {'password': user.password, 'points': 0}})
    return {"message": "User created successfully", "username": user.username}


@router.post("/login")
def login(user: User):
    print(users_db)
    if users_db[user.username]:
        if verify_password(user.password, users_db[user.username]['password']):
            return {"message": "Login successful"}
    raise HTTPException(status_code=401, detail="Invalid credentials")


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
