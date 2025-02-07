from uuid import UUID

from pydantic import BaseModel


class TaskReport(BaseModel):
    user_id: UUID
    task_id: UUID
    detail: str
