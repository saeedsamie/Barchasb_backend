# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
#
# from app.config import settings
# from app.models.Task import Task
# from app.models.User import User
#
# engine = create_engine(settings.TEST_DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()
#
#
# #     Base.metadata.create_all(bind=engine)  # Create tables for all models
# #     session = Session(bind=engine)
# #     yield session
# #     session.close()
# #     # Base.metadata.drop_all(bind=engine)
# #
# # engine = create_engine(settings.DATABASE_URL)
# # SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# # Base = declarative_base()
#
#
# def get_test_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
#
#
# def init_db():
#     Base.metadata.create_all(engine)
#     db = get_test_db()
#     user = User(name="updateduser", password="password123")
#     task = Task(type="image", data="Sample Data", point=10, tags=["urgent"])
#     db.add(user)
#     db.add(task)
#     db.commit()
