from datetime import datetime, timedelta

from fastapi import HTTPException
from jose import jwt, JWTError, ExpiredSignatureError

SECRET_KEY = "your-secret-key"  # Replace with a secure key in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = timedelta(minutes=5)  # Token expires after 30 minutes


def create_access_token(data: dict, expires_delta=ACCESS_TOKEN_EXPIRE_MINUTES):
    """
    Generates a JWT token with the given data and expiration time.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
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
