import logging
import os
from contextlib import contextmanager
from typing import Generator, Optional, AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy import create_engine, Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.sql import text

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create declarative base
Base = declarative_base()

class DatabaseManager:
    _instance: Optional['DatabaseManager'] = None
    _initialized: bool = False

    def __new__(cls, testing: bool = False) -> 'DatabaseManager':
        """Implement singleton pattern to ensure single database connection."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.testing = testing  # Set testing flag on first creation
        return cls._instance

    def __init__(self, testing: bool = False):
        """Initialize database connection and session maker."""
        # Skip if already initialized
        if self._initialized:
            return

        self._initialized = True
        self.database_url = self._get_database_url()
        self.engine = self._create_engine()
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        logger.info(f"Database Manager initialized in {'testing' if self.testing else 'production'} mode")

    def _get_database_url(self) -> str:
        """Get database URL from environment variables."""
        env_var = "TEST_DATABASE_URL" if self.testing else "DATABASE_URL"
        database_url = os.getenv(env_var)

        if not database_url:
            error_msg = f"{env_var} not found in environment variables"
            logger.error(error_msg)
            raise ValueError(error_msg)

        return database_url

    def _create_engine(self) -> Engine:
        """Create and configure database engine."""
        try:
            return create_engine(
                self.database_url,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=1800  # Recycle connections after 30 minutes
            )
        except Exception as e:
            error_msg = f"Failed to create database engine: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Context manager for database sessions."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            session.close()

    async def get_db(self) -> AsyncGenerator[Session, None]:
        """FastAPI dependency for database sessions."""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def init_db(self) -> None:
        """Initialize database schema."""
        try:
            Base.metadata.create_all(bind=self.engine)
            tables = list(Base.metadata.tables.keys())
            logger.info(f"Database initialized with tables: {tables}")
        except SQLAlchemyError as e:
            error_msg = f"Failed to initialize database: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def drop_db(self) -> None:
        """Drop all database tables."""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.info("Database tables dropped")
        except SQLAlchemyError as e:
            error_msg = f"Failed to drop database: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def check_connection(self) -> bool:
        """Check if database connection is working."""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                conn.commit()  # Ensure transaction is completed
                return True
        except SQLAlchemyError as e:
            logger.error(f"Database connection check failed: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in connection check: {str(e)}")
            return False

    def cleanup(self) -> None:
        """Cleanup database resources."""
        if hasattr(self, 'engine'):
            self.engine.dispose()
            delattr(self, 'engine')  # Remove engine attribute
            delattr(self, 'SessionLocal')  # Remove session maker
            self._initialized = False  # Allow re-initialization
            logger.info("Database resources cleaned up")

# Example usage:
# PRODUCTION_DB_URL = "postgresql://user:password@localhost/production_db"
# TEST_DB_URL = "sqlite:///test.db"
# db_manager = DatabaseManager(TEST_DB_URL)
# db_manager.init_db()  # Creates tables
