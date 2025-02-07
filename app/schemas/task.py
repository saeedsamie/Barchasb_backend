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
    is_done: bool = False
    tags: Optional[List[str]] = []

    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    type: str
    data: dict
    title: str = ""
    description: str = ""
    point: int
    is_done: bool = False
    tags: Optional[List[str]] = []


class TaskResponse(BaseModel):
    status: str
    task_id: UUID
