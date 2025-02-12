import uuid

from sqlalchemy import Column, Integer, String, UUID, ARRAY, Boolean
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from app.DatabaseManager import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String, nullable=False)
    data = Column(JSON, nullable=False)
    point = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=False)
    tags = Column(ARRAY(String))
    is_done = Column(Boolean, default=False)

    labels = relationship("TaskLabel", back_populates="task")  # List of labels belonging to a task
    reports = relationship("TaskReport", back_populates="task", cascade="all, delete-orphan")
