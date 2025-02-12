from typing import Optional, List, Dict
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator


class TaskBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "type": "image",
                "data": {"url": "https://example.com/image.jpg"},
                "title": "Sample Task",
                "description": "A test task",
                "point": 10,
                "tags": ["image", "labeling"]
            }
        }
    )

    id: Optional[UUID] = None
    type: str
    data: dict
    title: str
    description: str
    point: int = 10
    is_done: bool = False
    tags: Optional[List[str]] = []


class TaskCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "image",
                "data": {"url": "https://example.com/image.jpg"},
                "title": "New Task",
                "description": "Task description",
                "point": 10,
                "tags": ["urgent"]
            }
        }
    )

    type: str = Field(..., min_length=1, max_length=50)
    data: Dict = Field(..., description="Task data in JSON format")
    title: str = Field("", max_length=200)
    description: str = Field("", max_length=1000)
    point: int = Field(..., ge=0, le=1000)  # Points between 0 and 1000
    is_done: bool = False
    tags: Optional[List[str]] = []

    @field_validator('point')
    @classmethod
    def validate_points(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Points cannot be negative")
        return v

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v and len(v) > 10:  # Maximum 10 tags
            raise ValueError('Maximum 10 tags allowed')
        return v


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    status: str
    task_id: UUID


class TaskSubmission(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "content": {"label": "cat", "confidence": 0.95}
            }
        }
    )

    task_id: UUID
    user_id: UUID
    content: Dict = Field(..., description="Submission content")


class TaskFeedResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    tasks: List[TaskCreate]
    total: int
    has_more: bool = Field(
        default=False,
        description="Indicates if there are more tasks available"
    )
