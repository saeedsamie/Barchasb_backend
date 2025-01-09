import uuid

from sqlalchemy import Column, Integer, String, UUID, Text, ARRAY, Label
from sqlalchemy.orm import relationship, Session

from app.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String, nullable=False)
    data = Column(Text, nullable=False)
    point = Column(Integer, nullable=False)
    tags = Column(ARRAY(String))

    labels = relationship("Label", back_populates="task")

    @staticmethod
    def get_task_feed(db: Session):
        tasks = db.query(Task).all()
        return [
            {
                "id": str(task.id),
                "type": task.type,
                "data": task.data,
                "point": task.point,
                "tags": task.tags
            }
            for task in tasks
        ]

    @staticmethod
    def add_task(db: Session, type: str, data: str, point: int, tags: list = None):
        task = Task(type=type, data=data, point=point, tags=tags)
        db.add(task)
        db.commit()
        return {"status": "success", "task_id": str(task.id)}

    @staticmethod
    def list_done_tasks(db: Session):
        tasks = db.query(Task).filter(Task.labels.any(Label.content != None)).all()
        return [
            {
                "id": str(task.id),
                "type": task.type,
                "data": task.data,
                "point": task.point,
                "tags": task.tags
            }
            for task in tasks
        ]
