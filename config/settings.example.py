"""
Example settings file for trading backtest system.
Copy this file to settings.py and modify as needed.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
FMP_API_KEY = os.getenv('FMP_API_KEY', 'your_fmp_api_key_here')

# Database Configuration
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'trading_backtest'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'password'),
}

# Build database URL
DATABASE_URL = (
    f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}"
    f"@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}"
    f"/{DATABASE_CONFIG['database']}"
)

# Application Settings
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Cache Settings
CACHE_DURATION_HOURS = int(os.getenv('CACHE_DURATION_HOURS', 24))
MAX_CACHE_SIZE_MB = int(os.getenv('MAX_CACHE_SIZE_MB', 1000))

# Backtest Default Settings
DEFAULT_INITIAL_CAPITAL = float(os.getenv('DEFAULT_INITIAL_CAPITAL', 100000))
DEFAULT_COMMISSION = float(os.getenv('DEFAULT_COMMISSION', 0.001))
DEFAULT_SLIPPAGE = float(os.getenv('DEFAULT_SLIPPAGE', 0.0005))

# Logging Configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': LOG_LEVEL,
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': 'trading_backtest.log',
            'mode': 'a',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}
