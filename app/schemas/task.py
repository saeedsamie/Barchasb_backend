from typing import Optional, List, Dict
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator


class TaskBase(BaseModel):
    """
    Base schema for Task objects.
    
    Attributes:
        id: Optional UUID of the task
        type: Type of task (e.g., 'image', 'text')
        data: Task-specific data in dictionary format
        title: Title of the task
        description: Detailed description of the task
        point: Points awarded for completing the task
        is_done: Task completion status
        tags: Optional list of task tags
    """
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
    title: str = Field("", max_length=200)
    description: str = Field("", max_length=1000)
    point: int = Field(..., ge=0, le=1000)  # Points between 0 and 1000
    is_done: bool = False
    tags: Optional[List[str]] = []

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
        status: Response status
        task_id: UUID of the created/updated task
    """
    model_config = ConfigDict(from_attributes=True)
    
    status: str
    task_id: UUID


class TaskSubmission(BaseModel):
    """
    Schema for task submission.
    
    Attributes:
        task_id: UUID of the task being submitted
        user_id: UUID of the user submitting the task
        content: Submission content (e.g., labels, answers)
    """
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
    """
    Schema for paginated task feed response.
    
    Attributes:
        tasks: List of tasks in the feed
        total: Total number of tasks
        has_more: Whether there are more tasks available
    """
    model_config = ConfigDict(from_attributes=True)
    
    tasks: List[TaskCreate]
    total: int
    has_more: bool = Field(
        default=False,
        description="Indicates if there are more tasks available"
    )
