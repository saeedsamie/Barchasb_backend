import uuid

from sqlalchemy import Column, Integer, String, UUID
from sqlalchemy.orm import relationship

from app.DatabaseManager import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    points = Column(Integer, default=0)
    labeled_count = Column(Integer, default=0)

    labels = relationship("TaskLabel", back_populates="user")  # List of labels belonging to a user
