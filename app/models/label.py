import uuid

from sqlalchemy import Column, ForeignKey, UUID, Text
from sqlalchemy.orm import relationship, Session

from app.database import Base
from app.models.task import Task
from app.models.user import User


class Label(Base):
    __tablename__ = "labels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    content = Column(Text, nullable=False)

    user = relationship("User", back_populates="labels")
    task = relationship("Task", back_populates="labels")

    @staticmethod
    def submit_label(db: Session, user_id: uuid.UUID, task_id: uuid.UUID, content: str):
        label = Label(user_id=user_id, task_id=task_id, content=content)
        db.add(label)

        user = db.query(User).filter(User.id == user_id).first()
        task = db.query(Task).filter(Task.id == task_id).first()

        if user and task:
            user.points += task.point
            user.labeled_count += 1
            db.commit()
            return {
                "status": "success",
                "points_awarded": task.point
            }
        db.rollback()
        return {"status": "failure"}

    @staticmethod
    def calculate_consensus(db: Session, task_id: uuid.UUID):
        labels = db.query(Label).filter(Label.task_id == task_id).all()
        if labels:
            content_votes = {}
            for label in labels:
                content_votes[label.content] = content_votes.get(label.content, 0) + 1
            consensus = max(content_votes, key=content_votes.get)
            return {
                "task_id": str(task_id),
                "consensus": consensus,
                "votes": content_votes
            }
        return None

    @staticmethod
    def edit_labeled_task(db: Session, label_id: uuid.UUID, new_content: str):
        label = db.query(Label).filter(Label.id == label_id).first()
        if label:
            label.content = new_content
            db.commit()
            return {"status": "success"}
        return {"status": "failure"}

    @staticmethod
    def list_labeled_tasks_by_user(db: Session, user_id: uuid.UUID):
        labels = db.query(Label).filter(Label.user_id == user_id).all()
        return [
            {
                "label_id": str(label.id),
                "task_id": str(label.task_id),
                "content": label.content
            }
            for label in labels
        ]

    @staticmethod
    def list_reported_tasks_by_user(db: Session, user_id: uuid.UUID):
        labels = db.query(Label).filter(Label.user_id == user_id, Label.content.ilike("%reported%"))
        return [
            {
                "label_id": str(label.id),
                "task_id": str(label.task_id),
                "content": label.content
            }
            for label in labels
        ]
