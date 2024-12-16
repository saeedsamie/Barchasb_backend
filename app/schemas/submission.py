from pydantic import BaseModel


class SubmissionCreate(BaseModel):
    task_id: int
    user_id: int
    data: str
