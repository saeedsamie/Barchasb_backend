from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

Base = declarative_base()

DATABASE_URL: str = "postgresql://admin:admin@barchasb.bz91.ir:5432/barchasb_db"
TEST_DATABASE_URL: str = "postgresql://admin:admin@barchasb.bz91.ir:5432/test_barchasb_db"


class DatabaseManager:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        print("Database defined")

    def get_db(self) -> Generator[Session, None, None]:
        """
        Dependency for providing a database session in FastAPI routes.
        """
        print("Database generated")
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
