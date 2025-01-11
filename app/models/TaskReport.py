import uuid

from sqlalchemy import UUID, Column, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.DatabaseManager import Base


class TaskReport(Base):
    __tablename__ = "task_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    details = Column(Text, nullable=False)

    # Establish relationship to Task model
    task = relationship("Task", back_populates="reports")

    def __repr__(self):
        return f"<TaskReport(id={self.id}, task_id={self.task_id}, details={self.details[:20]}...)>"
