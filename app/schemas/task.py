# Task Schema
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel


class TaskBase(BaseModel):
    id: Optional[UUID]
    type: int
    data: dict
    title: str
    description: str
    point: int = 10
    tags: Optional[List[str]] = []

    class Config:
        orm_mode = True


class TaskCreate(BaseModel):
    type: int
    data: dict
    title: str
    description: str
    point: int = 10
    tags: Optional[List[str]] = []


class TaskResponse(TaskBase):
    pass
