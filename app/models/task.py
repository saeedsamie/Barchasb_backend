from sqlalchemy import Column, Integer, String, ForeignKey

from app.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    status = Column(String, default="open")
    assigned_to = Column(Integer, ForeignKey("users.id"))
