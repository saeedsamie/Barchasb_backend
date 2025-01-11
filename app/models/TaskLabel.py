import uuid

from sqlalchemy import Column, ForeignKey, UUID, Text
from sqlalchemy.orm import relationship

from app.DatabaseManager import Base


class TaskLabel(Base):
    __tablename__ = "labels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    content = Column(Text, nullable=False)

    user = relationship("User", back_populates="labels")
    task = relationship("Task", back_populates="labels")
