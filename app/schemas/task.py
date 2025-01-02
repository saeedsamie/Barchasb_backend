from pydantic import BaseModel


class TaskType:
    ASR_Task = 0
    Word_OCR = 1
    Sentence_OCR = 2


class Task(BaseModel):
    id: int
    type: int
    data: dict
    point: int = 10
    tags: str = ''


class Submission(BaseModel):
    id: int
    user_id: int
    task_id: int
    content: dict
