"""Initialize database for trading backtest system."""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.database import db_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_database():
    """Create database tables and initial setup."""
    try:
        logger.info("Creating database tables...")
        db_manager.create_tables()
        logger.info("Database setup completed successfully!")
    except Exception as e:
        logger.error(f"Failed to setup database: {e}")
        raise


if __name__ == "__main__":
    setup_database()