from uuid import UUID

from pydantic import BaseModel


class TaskReportCreate(BaseModel):
    task_id: UUID
    detail: str
