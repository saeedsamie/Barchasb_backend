from pydantic import BaseModel


class TaskCreate(BaseModel):
    description: str
    assigned_to: int


class TaskResponse(BaseModel):
    id: int
    description: str

    class Config:
        orm_mode = True
