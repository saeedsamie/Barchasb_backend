from typing import Optional, Dict
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


# Label Schema
class LabelBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: Optional[UUID] = None
    user_id: UUID
    task_id: UUID
    content: Dict = Field(..., description="Label content in JSON format")


class LabelCreate(BaseModel):
    task_id: UUID
    content: Dict = Field(
        ..., 
        description="Label content in JSON format",
        examples=[{"label": "cat", "confidence": 0.95}]
    )


class LabelResponse(LabelBase):
    pass
