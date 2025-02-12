from typing import Optional, List, Dict
from uuid import UUID

from pydantic import BaseModel, Field, validator


class TaskBase(BaseModel):
    id: Optional[UUID]
    type: str
    data: dict
    title: str
    description: str
    point: int = 10
    is_done: bool = False
    tags: Optional[List[str]] = []

    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    type: str = Field(..., min_length=1, max_length=50)
    data: Dict = Field(..., description="Task data in JSON format")
    title: str = Field("", max_length=200)
    description: str = Field("", max_length=1000)
    point: int = Field(..., ge=0, le=1000)  # Points between 0 and 1000
    is_done: bool = False
    tags: Optional[List[str]] = []

    @validator('point')
    def validate_points(cls, v):
        if v < 0:
            raise ValueError("Points cannot be negative")
        return v

    @validator('tags')
    def validate_tags(cls, v):
        if v and len(v) > 10:  # Maximum 10 tags
            raise ValueError('Maximum 10 tags allowed')
        return v


class TaskResponse(BaseModel):
    status: str
    task_id: UUID
