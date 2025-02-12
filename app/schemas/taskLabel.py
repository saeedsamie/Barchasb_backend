from typing import Optional, Dict
from uuid import UUID

from pydantic import BaseModel, Field


# Label Schema
class LabelBase(BaseModel):
    id: Optional[UUID]
    user_id: UUID
    task_id: UUID
    content: dict

    class Config:
        from_attributes = True


class LabelCreate(BaseModel):
    task_id: UUID
    user_id: UUID
    content: Dict = Field(..., description="Label content in JSON format")


class LabelResponse(LabelBase):
    pass
