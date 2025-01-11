from typing import Optional
from uuid import UUID

from pydantic import BaseModel


# Label Schema
class LabelBase(BaseModel):
    id: Optional[UUID]
    user_id: UUID
    task_id: UUID
    content: dict

    class Config:
        orm_mode = True


class LabelCreate(BaseModel):
    user_id: UUID
    task_id: UUID
    content: dict


class LabelResponse(LabelBase):
    pass
