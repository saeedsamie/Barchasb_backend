import os
import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

from app.DatabaseManager import DatabaseManager, Base
from app.models import User, Task  # Import models to ensure they're registered with Base

class TestDatabaseManager:
    @pytest.fixture(autouse=True)
    def setup_and_cleanup(self):
        """Setup before and cleanup after each test."""
        # Store original env vars
        self.original_db_url = os.getenv("DATABASE_URL")
        self.original_test_db_url = os.getenv("TEST_DATABASE_URL")
        
        # Set test environment variables
        # os.environ["TEST_DATABASE_URL"] = "postgresql://postgres:postgres@192.168.1.11:5432/test_db"
        # os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/prod_db"
        
        # Reset DatabaseManager singleton for each test
        DatabaseManager._instance = None
        DatabaseManager._initialized = False
        
        yield
        
        # Cleanup
        if hasattr(DatabaseManager._instance, 'engine'):
            DatabaseManager._instance.cleanup()
        
        if self.original_db_url:
            os.environ["DATABASE_URL"] = self.original_db_url
        if self.original_test_db_url:
            os.environ["TEST_DATABASE_URL"] = self.original_test_db_url

    def test_singleton_pattern(self):
        """Test that DatabaseManager implements singleton pattern correctly."""
        db1 = DatabaseManager(testing=False)  # Production mode
        db2 = DatabaseManager(testing=False)  # Should return same instance
        assert db1 is db2
        assert not db1.testing
        
        # Reset singleton for testing mode test
        DatabaseManager._instance = None
        DatabaseManager._initialized = False
        
        db3 = DatabaseManager(testing=True)  # Testing mode
        db4 = DatabaseManager(testing=True)  # Should return same instance
        assert db3 is db4
        assert db3.testing

    def test_initialization_with_invalid_url(self):
        """Test initialization with invalid database URL."""
        os.environ["TEST_DATABASE_URL"] = "invalid://url"
        DatabaseManager._instance = None  # Reset singleton
        with pytest.raises((RuntimeError, SQLAlchemyError)) as exc_info:
            DatabaseManager(testing=True)
        assert "Failed to create" in str(exc_info.value)

    def test_missing_database_url(self):
        """Test initialization with missing database URL."""
        if "TEST_DATABASE_URL" in os.environ:
            del os.environ["TEST_DATABASE_URL"]
        DatabaseManager._instance = None  # Reset singleton
        with pytest.raises(ValueError) as exc_info:
            DatabaseManager(testing=True)
        assert "not found in environment variables" in str(exc_info.value)

    def test_database_operations(self):
        """Test basic database operations."""
        db_manager = DatabaseManager(testing=True)
        
        # Test initialization
        db_manager.init_db()
        
        # Test session creation and basic query
        with db_manager.get_session() as session:
            # Create a test user
            test_user = User(
                name="test_user",
                password="hashed_password",
                points=0
            )
            session.add(test_user)
            session.commit()
            
            # Query the user back
            queried_user = session.query(User).filter_by(name="test_user").first()
            assert queried_user is not None
            assert queried_user.name == "test_user"

    def test_connection_check(self):
        """Test database connection check functionality."""
        db_manager = DatabaseManager(testing=True)
        assert db_manager.check_connection() is True
        
        # Test with invalid connection
        db_manager.cleanup()  # Clean up existing connection
        DatabaseManager._instance = None  # Reset singleton
        DatabaseManager._initialized = False
        
        # Set invalid URL in environment
        original_url = os.getenv("TEST_DATABASE_URL")
        os.environ["TEST_DATABASE_URL"] = "postgresql://invalid:invalid@localhost:5432/invalid_db"
        
        try:
            db_manager = DatabaseManager(testing=True)
            assert db_manager.check_connection() is False
        finally:
            # Restore original URL
            if original_url:
                os.environ["TEST_DATABASE_URL"] = original_url
            else:
                del os.environ["TEST_DATABASE_URL"]

    def test_session_context_manager(self):
        """Test session context manager with transaction rollback."""
        db_manager = DatabaseManager(testing=True)
        db_manager.init_db()
        
        # Test successful transaction
        with db_manager.get_session() as session:
            test_user = User(
                name="test_user_2",
                password="hashed_password",
                points=0
            )
            session.add(test_user)
        
        # Verify user was saved
        with db_manager.get_session() as session:
            saved_user = session.query(User).filter_by(name="test_user_2").first()
            assert saved_user is not None
        
        # Test transaction rollback
        with pytest.raises(SQLAlchemyError):
            with db_manager.get_session() as session:
                test_user = User(
                    name="test_user_3",
                    password="hashed_password",
                    points=0
                )
                session.add(test_user)
                session.execute(text("INVALID SQL"))  # This will cause an error
        
        # Verify user was not saved due to rollback
        with db_manager.get_session() as session:
            rolled_back_user = session.query(User).filter_by(name="test_user_3").first()
            assert rolled_back_user is None

    def test_cleanup(self):
        """Test database cleanup functionality."""
        db_manager = DatabaseManager(testing=True)
        db_manager.init_db()
        
        # Create some test data
        with db_manager.get_session() as session:
            test_user = User(
                name="cleanup_test",
                password="hashed_password",
                points=0
            )
            session.add(test_user)
        
        # Test cleanup
        db_manager.cleanup()
        
        # Verify connection is disposed
        assert not hasattr(db_manager, 'engine')
        assert not hasattr(db_manager, 'SessionLocal')
        assert not db_manager._initialized

    def test_drop_db(self):
        """Test database drop functionality."""
        db_manager = DatabaseManager(testing=True)
        db_manager.init_db()
        
        # Create some test data
        with db_manager.get_session() as session:
            test_user = User(
                name="drop_test",
                password="hashed_password",
                points=0
            )
            session.add(test_user)
        
        # Drop database
        db_manager.drop_db()
        
        # Verify tables are dropped
        with db_manager.engine.connect() as conn:
            result = conn.execute(text(
                "SELECT EXISTS (SELECT FROM information_schema.tables "
                "WHERE table_name = 'users')"
            ))
            assert not result.scalar()

    @pytest.mark.asyncio
    async def test_fastapi_dependency(self):
        """Test the FastAPI dependency injection."""
        db_manager = DatabaseManager(testing=True)
        db_manager.init_db()
        
        # Test the FastAPI dependency directly
        async def test_endpoint():
            db = None
            async for session in db_manager.get_db():
                db = session
            return db
        
        try:
            db = await test_endpoint()
            assert db is not None
            
            # Test basic query
            test_user = User(
                name="dependency_test",
                password="hashed_password",
                points=0
            )
            db.add(test_user)
            db.commit()
            
            queried_user = db.query(User).filter_by(name="dependency_test").first()
            assert queried_user is not None
        finally:
            if db:
                db.close() 