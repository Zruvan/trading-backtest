"""Application constants."""

# API endpoints
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"

# Database settings
DEFAULT_DB_POOL_SIZE = 10
DEFAULT_DB_MAX_OVERFLOW = 20

# Cache settings
DEFAULT_CACHE_DURATION_HOURS = 24
MAX_CACHE_SIZE_MB = 1000

# Market data
TRADING_DAYS_PER_YEAR = 252
HOURS_PER_TRADING_DAY = 6.5

# Risk-free rate (approximate US Treasury 3-month rate)
RISK_FREE_RATE = 0.02

# Default backtest settings
DEFAULT_INITIAL_CAPITAL = 100000
DEFAULT_COMMISSION = 0.001  # 0.1%
DEFAULT_SLIPPAGE = 0.0005   # 0.05%

# Rebalance frequencies
REBALANCE_FREQUENCIES = {
    'daily': 1,
    'weekly': 5,
    'monthly': 21,
    'quarterly': 63,
    'annually': 252
}

# Stock screening parameters
MIN_MARKET_CAP = 1e9  # $1 billion minimum market cap
MIN_VOLUME = 1e6      # $1 million daily volume minimum
MIN_PRICE = 5.0       # $5 minimum stock price

# API rate limits
FMP_RATE_LIMIT_PER_MINUTE = 250
FMP_RATE_LIMIT_PER_DAY = 10000
