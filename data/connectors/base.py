"""Base connector class for data sources."""
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import pandas as pd
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class BaseConnector(ABC):
    """Base class for data source connectors."""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize connector.
        
        Args:
            api_key: API key for authentication
            **kwargs: Additional connector-specific parameters
        """
        self.api_key = api_key
        self.session = None
        self._setup_session(**kwargs)
    
    def _setup_session(self, **kwargs):
        """Set up HTTP session with default configuration."""
        import requests
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': 'trading-backtest/1.0',
            'Accept': 'application/json',
        })
        
        # Configure timeouts and retries
        timeout = kwargs.get('timeout', 30)
        self.session.timeout = timeout
    
    @abstractmethod
    def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get basic stock information.
        
        Args:
            symbol: Stock ticker symbol
        
        Returns:
            Dictionary with stock information
        """
        pass
    
    @abstractmethod
    def get_historical_prices(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> pd.DataFrame:
        """
        Get historical price data.
        
        Args:
            symbol: Stock ticker symbol
            start_date: Start date for data
            end_date: End date for data
        
        Returns:
            DataFrame with price data
        """
        pass
    
    @abstractmethod
    def get_fundamentals(
        self,
        symbol: str,
        period: str = 'annual'
    ) -> Dict[str, Any]:
        """
        Get fundamental data.
        
        Args:
            symbol: Stock ticker symbol
            period: Period for fundamentals ('annual' or 'quarterly')
        
        Returns:
            Dictionary with fundamental data
        """
        pass
    
    @abstractmethod
    def get_stock_list(self) -> List[Dict[str, Any]]:
        """
        Get list of available stocks.
        
        Returns:
            List of dictionaries with stock information
        """
        pass
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        Validate if a stock symbol exists.
        
        Args:
            symbol: Stock ticker symbol
        
        Returns:
            True if symbol is valid, False otherwise
        """
        try:
            info = self.get_stock_info(symbol)
            return info is not None and len(info) > 0
        except Exception as e:
            logger.warning(f"Symbol validation failed for {symbol}: {e}")
            return False
    
    def get_multiple_historical_prices(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, pd.DataFrame]:
        """
        Get historical prices for multiple symbols.
        
        Args:
            symbols: List of stock ticker symbols
            start_date: Start date for data
            end_date: End date for data
        
        Returns:
            Dictionary mapping symbols to price DataFrames
        """
        result = {}
        for symbol in symbols:
            try:
                result[symbol] = self.get_historical_prices(symbol, start_date, end_date)
                logger.debug(f"Retrieved price data for {symbol}")
            except Exception as e:
                logger.error(f"Failed to get price data for {symbol}: {e}")
                result[symbol] = pd.DataFrame()
        
        return result
    
    def close(self):
        """Close the connector and clean up resources."""
        if self.session:
            self.session.close()
            self.session = None
