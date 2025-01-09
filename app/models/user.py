import uuid

from sqlalchemy import Column, Integer, String, UUID
from sqlalchemy.orm import relationship, Session

from app.database import Base
from app.services.JWT_helper import create_access_token
from app.services.hash_helper import check_password_hash, generate_password_hash


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)  # Stored as a hash
    points = Column(Integer, default=0)
    labeled_count = Column(Integer, default=0)

    labels = relationship("Label", back_populates="user")

    @staticmethod
    def signup(db: Session, name: str, password: str):
        hashed_password = generate_password_hash(password)
        user = User(name=name, password=hashed_password)
        db.add(user)
        db.commit()
        return {"status": "success", "user_id": str(user.id)}

    @staticmethod
    def login(db: Session, name: str, password: str):
        user = db.query(User).filter(User.name == name).first()
        if user and check_password_hash(user.password, password):
            token = create_access_token({"user_id": str(user.id)})
            return {"status": "success", "token": token}
        return {"status": "failure", "message": "Invalid credentials"}

    @staticmethod
    def get_information(db: Session, user_id: uuid.UUID):
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            return {
                "user_id": str(user.id),
                "name": user.name,
                "points": user.points,
                "labeled_count": user.labeled_count
            }
        return None

    @staticmethod
    def change_information(db: Session, user_id: uuid.UUID, new_name: str = None):
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            if new_name:
                user.name = new_name
            db.commit()
            return {"status": "success"}
        return {"status": "failure"}

    @staticmethod
    def change_password(db: Session, user_id: uuid.UUID, new_password: str):
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.password = generate_password_hash(new_password)
            db.commit()
            return {"status": "success"}
        return {"status": "failure"}
