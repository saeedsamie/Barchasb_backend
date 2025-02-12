import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from fastapi import HTTPException
from jose import jwt, JWTError, ExpiredSignatureError

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = timedelta(minutes=15)


def create_access_token(data: dict, expires_delta=ACCESS_TOKEN_EXPIRE_MINUTES):
    """
    Generates a JWT token with the given data and expiration time.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: str):
    """
    Generates a refresh token with a 5-min expiration.
    """
    return create_access_token({"user_id": user_id}, expires_delta=timedelta(minutes=5))


def decode_access_token(token: str):
    """
    Decodes and validates a JWT token.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired"
        )
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
