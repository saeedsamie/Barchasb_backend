from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class User(BaseModel):
    name: str
    password: str
    points: int = 0


class UserCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=8, max_length=128, description="Password must be strong")

    @field_validator("password")
    def validate_password_strength(cls, password):
        if not any(char.isdigit() for char in password):
            raise ValueError("Password must include at least one number")
        if not any(char.isalpha() for char in password):
            raise ValueError("Password must include at least one letter")
        if not any(char in "!@#$%^&*()-_=+" for char in password):
            raise ValueError("Password must include at least one special character")
        return password


class UserResponse(BaseModel):
    id: UUID
    name: str
    points: int
    labeled_count: int

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    user: UserResponse
    token: str

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    new_name: str

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    name: str
    password: str

    class Config:
        from_attributes = True


class UserChangePassword(BaseModel):
    new_password: str

    class Config:
        from_attributes = True
