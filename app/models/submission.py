from sqlalchemy import Column, Integer, String, ForeignKey

from app.database import Base


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    data = Column(String)
    status = Column(String, default="pending")
