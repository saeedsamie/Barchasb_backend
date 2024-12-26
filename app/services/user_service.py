from passlib.context import CryptContext

from app.schemas.user import UserCreate, User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_user(user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    return User(username=user.username, password=hashed_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
