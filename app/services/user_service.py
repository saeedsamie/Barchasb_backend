import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.User import User
from app.services.JWT_helper import create_access_token
from app.services.hash_helper import check_password_hash, generate_password_hash


class UserAlreadyExistsError(Exception):
    """
    Custom exception raised when a user with the same username already exists.
    """

    def __init__(self, username: str):
        self.username = username
        self.message = f"User with name '{username}' already exists."
        super().__init__(self.message)

    def __str__(self):
        return self.message


def create_user(db: Session, name: str, password: str) -> User:
    """
    Create a new user in the database.

    Raises:
        UserAlreadyExistsError: If a user with the same username already exists.
    """
    hashed_password = generate_password_hash(password)
    user = User(name=name, password=hashed_password)
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError as e:
        db.rollback()
        if "unique constraint" in str(e):
            raise UserAlreadyExistsError(name)
        raise e  # Reraise other IntegrityErrors


def login_user(db: Session, name: str, password: str) -> tuple[User, str]:
    """
    Authenticate a user and return the user object along with a JWT token.
    """
    user = db.query(User).filter(User.name == name).first()
    if user and check_password_hash(user.password, password):
        token = create_access_token({"user_id": str(user.id)})
        return user, token
    raise Exception("Invalid credentials")


def get_information(db: Session, user_id: uuid.UUID) -> User:
    """
    Fetch user information by ID.
    """
    user = db.query(User).filter(User.id == user_id).first()
    return user  # Let routers or other layers handle serialization


def change_information(db: Session, user_id: uuid.UUID, new_name: str = None) -> User:
    """
    Update user information (e.g., name).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user and new_name:
        user.name = new_name
        db.commit()
    return user  # Return the updated user or None if not found


def change_password(db: Session, user_id: uuid.UUID, new_password: str) -> User:
    """
    Update user password.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.password = generate_password_hash(new_password)
        db.commit()
    return user  # Return the updated user or None if not found
