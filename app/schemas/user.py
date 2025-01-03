from pydantic import BaseModel, Field, field_validator


class User(BaseModel):
    username: str
    password: str
    points: int = 0


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
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
