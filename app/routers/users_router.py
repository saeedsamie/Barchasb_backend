import uuid

from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.DatabaseManager import DatabaseManager
from app.controller.user_controller import (
    create_user,
    login_user,
    get_information,
    change_information,
    change_password, get_leaderboard)
from app.schemas.user import UserCreate, UserUpdate, UserLogin, UserChangePassword
from app.utils.JWT_helper import decode_access_token

# Initialize the database manager
db_manager = DatabaseManager()

router = APIRouter(prefix="/users")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(db_manager.get_db)):
    payload = decode_access_token(token)
    user = get_information(db, user_id=uuid.UUID(payload["user_id"]))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/signup", response_model=dict, status_code=201)
async def create_user_route(user: UserCreate, db: Session = Depends(db_manager.get_db)):
    try:
        created_user = create_user(db, name=user.name, password=user.password, points=user.points)
        return {"id": str(created_user.id), "name": created_user.name}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=dict)
async def login_user_route(user: UserLogin = Body(...), db: Session = Depends(db_manager.get_db)):
    try:
        _, token = login_user(db, name=user.name, password=user.password)
        return {"access_token": token}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/leaderboard", response_model=list)
async def get_leader_board(current_user: dict = Depends(get_current_user),
                     db: Session = Depends(db_manager.get_db)):
    """
    Retrieve a list of users sorted by points in descending order.
    """
    try:
        users = get_leaderboard(db)
        return [
            {"id": user.id,
             "name": user.name,
             "points": user.points,
             "labeled_count": user.labeled_count} for user in users
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch leaderboard: {str(e)}")


@router.get("/user/", response_model=dict)
async def get_user_information(current_user=Depends(get_current_user), db: Session = Depends(db_manager.get_db)):
    user = current_user
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {'id': user.id, 'name': user.name, 'points': user.points, 'label_count': user.labeled_count}


@router.put("/user/", response_model=dict)
def update_user_information(user_update: UserUpdate, current_user=Depends(get_current_user),
                            db: Session = Depends(db_manager.get_db)):
    user = change_information(db, user_id=current_user.id, new_name=user_update.new_name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {'id': user.id, 'name': user.name, 'points': user.points, 'label_count': user.labeled_count}


@router.put("/user/password", response_model=dict)
async def update_user_password(user_password: UserChangePassword, current_user=Depends(get_current_user),
                         db: Session = Depends(db_manager.get_db)):
    user = change_password(db, user_id=current_user.id, new_password=user_password.new_password)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {'id': user.id, 'result': "Password updated"}
