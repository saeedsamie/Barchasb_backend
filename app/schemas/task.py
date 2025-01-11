from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel


class TaskBase(BaseModel):
    id: Optional[UUID]
    type: str
    data: dict
    title: str
    description: str
    point: int = 10
    tags: Optional[List[str]] = []

    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    type: str
    data: dict
    title: str = ""
    description: str = ""
    point: int
    tags: Optional[List[str]] = []


class TaskResponse(BaseModel):
    status: str
    task_id: UUID
