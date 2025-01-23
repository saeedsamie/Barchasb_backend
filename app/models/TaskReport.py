import uuid

from sqlalchemy import UUID, Column, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.DatabaseManager import Base


class TaskReport(Base):
    __tablename__ = "task_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    details = Column(Text, nullable=False)

    user = relationship("User", back_populates="reports")
    task = relationship("Task", back_populates="reports")
