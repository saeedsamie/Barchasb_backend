import uuid

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from starlette import status

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.services.JWT_helper import decode_access_token, create_expired_access_token

router = APIRouter()

users_db = dict()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    response = User.signup(db=db, name=user.name, password=user.password)
    if response["status"] == "failure":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
    user_id = response["user_id"]
    db_user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    return UserResponse(id=db_user.id, name=db_user.name, points=db_user.points, labeled_count=db_user.labeled_count)


@router.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    response = User.login(db=db, name=user.name, password=user.password)
    if response["status"] == "failure":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    return {"access_token": response["token"], "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_user_info(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user_id = payload.get("user_id")
    db_user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse(id=db_user.id, name=db_user.name, points=db_user.points, labeled_count=db_user.labeled_count)


@router.post("/logout")
def logout(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    expired_token = create_expired_access_token(payload=payload)
    return {"message": "Successfully logged out", "expired_token": expired_token}
