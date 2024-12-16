from pydantic import BaseModel


class Task(BaseModel):
    id: int
    title: str
    description: str
    total_labels: int = 0


class Submission(BaseModel):
    task_id: int
    user: str
    label: str
