from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from app.DatabaseManager import DatabaseManager
from app.controller.user_controller import (
    create_user,
    login_user,
    get_information,
    change_information,
    change_password, get_leaderboard)
from app.schemas.user import UserCreate, UserUpdate, UserLogin, UserChangePassword

# Initialize the database manager
db_manager = DatabaseManager()

router = APIRouter(prefix="/users")


@router.post("/signup", response_model=dict)
def create_user_route(user: UserCreate, db: Session = Depends(db_manager.get_db)):
    try:
        created_user = create_user(db, name=user.name, password=user.password, points=user.points)
        return {"id": str(created_user.id), "name": created_user.name}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=dict)
def login_user_route(user: UserLogin = Body(...), db: Session = Depends(db_manager.get_db)):
    try:
        _, token = login_user(db, name=user.name, password=user.password)
        return {"access_token": token}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/leaderboard", response_model=list)
def get_leader_board(db: Session = Depends(db_manager.get_db)):
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


@router.get("/{user_id}", response_model=dict)
def get_user_information(user_id: str, db: Session = Depends(db_manager.get_db)):
    try:
        user_uuid = UUID(user_id)  # Validate UUID format
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    user = get_information(db, user_id=user_uuid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {'id': user.id, 'name': user.name, 'points': user.points, 'label_count': user.labeled_count}


@router.put("/{user_id}", response_model=dict)
def update_user_information(user_id: str, user_update: UserUpdate, db: Session = Depends(db_manager.get_db)):
    try:
        user_uuid = UUID(user_id)  # Validate UUID format
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    user = change_information(db, user_id=user_uuid, new_name=user_update.new_name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {'id': user.id, 'name': user.name, 'points': user.points, 'label_count': user.labeled_count}


@router.put("/{user_id}/password", response_model=dict)
def update_user_password(user_id: str, user_password: UserChangePassword, db: Session = Depends(db_manager.get_db)):
    try:
        user_uuid = UUID(user_id)  # Validate UUID format
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    user = change_password(db, user_id=user_uuid, new_password=user_password.new_password)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {'id': user.id, 'result': "Password updated"}
