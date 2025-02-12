from uuid import UUID

from pydantic import BaseModel, Field


class TaskReport(BaseModel):
    task_id: UUID
    user_id: UUID
    detail: str = Field(..., min_length=1, max_length=1000)
