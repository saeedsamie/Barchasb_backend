import uuid

from sqlalchemy import Column, Integer, String, UUID
from sqlalchemy.orm import relationship

from app.DatabaseManager import Base


class User(Base):
    """
    User model representing application users.

    Attributes:
        id (UUID): Unique identifier for the user
        name (str): Unique username
        password (str): Hashed password
        points (int): Points earned by the user
        labeled_count (int): Number of tasks labeled by the user
        labels (relationship): One-to-many relationship with TaskLabel
        reports (relationship): One-to-many relationship with TaskReport
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    points = Column(Integer, default=0)
    labeled_count = Column(Integer, default=0)

    labels = relationship("TaskLabel", back_populates="user")  # List of labels belonging to a user
    reports = relationship("TaskReport", back_populates="user")  # List of reports created by the user
