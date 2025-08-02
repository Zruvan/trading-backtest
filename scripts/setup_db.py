"""Initialize database for trading backtest system."""
import sys
import os
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data.database import init_database, DatabaseManager
from data.models import Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_database():
    """Set up the database with all required tables."""
    try:
        # Import settings
        try:
            from config.settings import DATABASE_URL
        except ImportError:
            # Fallback to SQLite if no settings file
            logger.warning("No settings file found, using SQLite database")
            DATABASE_URL = "sqlite:///trading_backtest.db"
        
        logger.info(f"Initializing database: {DATABASE_URL}")
        
        # Initialize database manager
        db_manager = init_database(DATABASE_URL)
        
        # Test connection
        if not db_manager.health_check():
            logger.error("Database health check failed")
            return False
        
        logger.info("Database connection successful")
        
        # Create all tables
        logger.info("Creating database tables...")
        db_manager.create_tables()
        
        logger.info("Database setup completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        return False


def create_timescale_init_script():
    """Create initialization script for TimescaleDB."""
    init_script = """
-- TimescaleDB initialization script
-- This script is automatically run when PostgreSQL container starts

-- Create TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Create hypertables for time-series data after tables are created
-- Note: These will be created by the application after table creation
"""
    
    scripts_dir = project_root / "scripts"
    scripts_dir.mkdir(exist_ok=True)
    
    init_file = scripts_dir / "init_timescale.sql"
    with open(init_file, 'w') as f:
        f.write(init_script)
    
    logger.info(f"Created TimescaleDB init script: {init_file}")


def main():
    """Main function."""
    logger.info("Starting database setup...")
    
    # Create TimescaleDB initialization script
    create_timescale_init_script()
    
    # Set up database
    success = setup_database()
    
    if success:
        logger.info("Database setup completed successfully!")
        print("\n✅ Database setup completed!")
        print("🔹 All tables created successfully")
        print("🔹 Database is ready for use")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and add your FMP API key")
        print("2. Copy config/settings.example.py to config/settings.py")
        print("3. Run an example strategy: python scripts/examples/market_cap_strategy.py")
    else:
        logger.error("Database setup failed!")
        print("\n❌ Database setup failed!")
        print("🔹 Check the logs above for error details")
        print("🔹 Ensure database is accessible")
        print("🔹 Check your database configuration in .env or settings.py")
        sys.exit(1)


if __name__ == "__main__":
    main()