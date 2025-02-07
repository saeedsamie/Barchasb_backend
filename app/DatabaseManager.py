import os
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base

Base = declarative_base()
load_dotenv()


class DatabaseManager:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        print("Database Manager initialized")

    def get_db(self) -> Generator[Session, None, None]:
        """
        Dependency for providing a database session in FastAPI routes.
        """
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def init_db(self):
        """
        Create all tables.
        """
        print("Database initialized")
        Base.metadata.create_all(bind=self.engine)
        print("Registered tables:", Base.metadata.tables.keys())

    def drop_db(self):
        """
        Drop all tables.
        """
        print("Database dropped")
        Base.metadata.drop_all(bind=self.engine)

# Example usage:
# PRODUCTION_DB_URL = "postgresql://user:password@localhost/production_db"
# TEST_DB_URL = "sqlite:///test.db"
# db_manager = DatabaseManager(TEST_DB_URL)
# db_manager.init_db()  # Creates tables
