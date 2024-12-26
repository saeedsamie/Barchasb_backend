from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from starlette import status

from app.schemas.user import User, UserCreate
from app.services.JWT_helper import create_access_token, decode_access_token
from app.services.user_service import verify_password, create_user

router = APIRouter()

users_db = dict()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate):
    if user.username in users_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Username already exists')
    new_user = create_user(user)
    users_db.update({new_user.username: {'password': new_user.password, 'points': 0}})
    return {"message": "User created successfully", "username": new_user.username}


@router.post("/login")
async def login(user: User):
    user_data = users_db.get(user.username)
    # client_ip = get_client_ip(request)

    if not user_data or not verify_password(user.password, user_data['password']):
        # logger.warning(
        #     f"Invalid login attempt for username: {user.username}, IP: {client_ip}"
        # )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Create a JWT token
    access_token = create_access_token(data={"sub": user.username})

    # logger.info(f"Successful login for username: {user.username}, IP: {client_ip}")
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/protected-route")
def protected_route(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"message": f"Welcome, {payload['sub']}!"}


def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return payload.get("sub")


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
