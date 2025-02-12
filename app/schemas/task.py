from typing import Optional, List, Dict
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, field_validator


class TaskCreate(BaseModel):
    """
    Schema for creating new tasks.
    
    Attributes:
        type: Type of task (1-50 characters)
        data: Task data in JSON format
        title: Task title (max 200 characters)
        description: Task description (max 1000 characters)
        point: Points for task (0-1000)
        is_done: Task completion status
        tags: Optional list of tags (max 10 tags)
    """
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
    point: int = Field(..., ge=0, le=1000)  # Points between 0 and 1000
    title: str = Field("", max_length=200)
    description: str = Field("", max_length=1000)
    tags: Optional[List[str]] = []
    is_done: bool = False

    @field_validator('point')
    @classmethod
    def validate_points(cls, v: int) -> int:
        """Validate that points are not negative."""
        if v < 0:
            raise ValueError("Points cannot be negative")
        return v

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate that there are not too many tags."""
        if v and len(v) > 10:  # Maximum 10 tags
            raise ValueError('Maximum 10 tags allowed')
        return v


class TaskResponse(BaseModel):
    """
        Schema for task response.

        Attributes:
            id: UUID of the created/updated task
            type: Type of task (1-50 characters)
            data: Task data in JSON format
            title: Task title (max 200 characters)
            description: Task description (max 1000 characters)
            point: Points for task (0-1000)
            is_done: Task completion status
            tags: Optional list of tags (max 10 tags)
        """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "type": "image",
                "data": {"url": "https://example.com/image.jpg"},
                "title": "New Task",
                "description": "Task description",
                "point": 10,
                "tags": ["urgent"]
            }
        }
    )
    id: UUID
    type: str = Field(..., min_length=1, max_length=50)
    data: Dict = Field(..., description="Task data in JSON format")
    point: int = Field(..., ge=0, le=1000)  # Points between 0 and 1000
    title: str = Field("", max_length=200)
    description: str = Field("", max_length=1000)
    tags: Optional[List[str]] = []
    is_done: bool = False

    @field_validator('point')
    @classmethod
    def validate_points(cls, v: int) -> int:
        """Validate that points are not negative."""
        if v < 0:
            raise ValueError("Points cannot be negative")
        return v

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate that there are not too many tags."""
        if v and len(v) > 10:  # Maximum 10 tags
            raise ValueError('Maximum 10 tags allowed')
        return v


class TaskSubmission(BaseModel):
    """
    Schema for task submission.
    
    Attributes:
        task_id: UUID of the task being submitted
        content: Submission content (e.g., labels, answers)
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "task_id": "123e4567-e89b-12d3-a456-426614174000",
                "content": {"label": "cat", "confidence": 0.95}
            }
        }
    )

    task_id: UUID
    content: Dict = Field(..., description="Submission content")


class TaskFeedResponse(BaseModel):
    """
    Schema for paginated task feed response.
    
    Attributes:
        tasks: List of tasks in the feed
        total: Total number of tasks
        has_more: Whether there are more tasks available
    """
    model_config = ConfigDict(from_attributes=True)

    tasks: List[TaskResponse]
    total: int
    has_more: bool = Field(
        default=False,
        description="Indicates if there are more tasks available"
    )
