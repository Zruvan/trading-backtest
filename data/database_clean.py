"""Database connection and session management."""
import logging
from contextlib import contextmanager
from typing import Optional
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from data.models import Base

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and sessions."""
    
    def __init__(self, database_url: str, **kwargs):
        """
        Initialize database manager.
        
        Args:
            database_url: SQLAlchemy database URL
            **kwargs: Additional SQLAlchemy engine parameters
        """
        self.database_url = database_url
        
        # Default engine configuration
        engine_config = {
            'poolclass': QueuePool,
            'pool_size': kwargs.get('pool_size', 10),
            'max_overflow': kwargs.get('max_overflow', 20),
            'pool_pre_ping': True,
            'echo': kwargs.get('echo', False),
        }
        
        # Create engine
        self.engine = create_engine(database_url, **engine_config)
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False
        )
        
        # Set up event listeners
        self._setup_event_listeners()
    
    def _setup_event_listeners(self):
        """Set up SQLAlchemy event listeners."""
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Set SQLite pragmas if using SQLite."""
            if 'sqlite' in self.database_url:
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

    def create_tables(self):
        """Create all database tables defined in models."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
            
            # Create TimescaleDB hypertables if using PostgreSQL
            if 'postgresql' in self.database_url.lower():
                self._create_hypertables()
                
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise
    
    def _create_hypertables(self):
        """Create TimescaleDB hypertables for time-series data."""
        try:
            from sqlalchemy import text
            with self.get_session() as session:
                # Create hypertable for price_data if it doesn't exist
                session.execute(text("""
                    SELECT create_hypertable('price_data', 'date', 
                           chunk_time_interval => INTERVAL '1 month',
                           if_not_exists => TRUE);
                """))
                
                # Create hypertable for portfolio_snapshots if it doesn't exist
                session.execute(text("""
                    SELECT create_hypertable('portfolio_snapshots', 'date',
                           chunk_time_interval => INTERVAL '1 month', 
                           if_not_exists => TRUE);
                """))
                
                session.commit()
                logger.info("TimescaleDB hypertables created successfully")
        except Exception as e:
            logger.warning(f"Could not create TimescaleDB hypertables (normal if not using TimescaleDB): {e}")

    def drop_tables(self):
        """Drop all database tables."""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.info("Database tables dropped successfully")
        except Exception as e:
            logger.error(f"Error dropping database tables: {e}")
            raise

    @contextmanager
    def get_session(self):
        """
        Get a database session with automatic cleanup.
        
        Yields:
            SQLAlchemy session
        """
        session = self.SessionLocal()
        try:
            yield session
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def get_session_sync(self) -> Session:
        """
        Get a database session (caller responsible for cleanup).
        
        Returns:
            SQLAlchemy session
        """
        return self.SessionLocal()
    
    def health_check(self) -> bool:
        """
        Check database connectivity.
        
        Returns:
            True if database is accessible, False otherwise
        """
        try:
            from sqlalchemy import text
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def close(self):
        """Close database connections."""
        if hasattr(self, 'engine'):
            self.engine.dispose()
            logger.info("Database connections closed")


# Global database instance (will be initialized by application)
db_manager: Optional[DatabaseManager] = None


def init_database(database_url: str, **kwargs) -> DatabaseManager:
    """
    Initialize global database manager.
    
    Args:
        database_url: SQLAlchemy database URL
        **kwargs: Additional engine parameters
    
    Returns:
        DatabaseManager instance
    """
    global db_manager
    db_manager = DatabaseManager(database_url, **kwargs)
    return db_manager


def get_db_session():
    """
    Get database session from global manager.
    
    Returns:
        SQLAlchemy session
    """
    if db_manager is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return db_manager.get_session_sync()


@contextmanager
def get_db_session_context():
    """
    Get database session with context manager.
    
    Yields:
        SQLAlchemy session
    """
    if db_manager is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    with db_manager.get_session() as session:
        yield session
