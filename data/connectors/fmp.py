"""Financial Modeling Prep API connector."""
import logging
from typing import Dict, List, Optional, Any
import pandas as pd
from datetime import datetime, timedelta
import time
from data.connectors.base import BaseConnector
from config.constants import FMP_BASE_URL, FMP_RATE_LIMIT_PER_MINUTE

logger = logging.getLogger(__name__)


class FMPConnector(BaseConnector):
    """Financial Modeling Prep API connector."""
    
    def __init__(self, api_key: str, **kwargs):
        """
        Initialize FMP connector.
        
        Args:
            api_key: FMP API key
            **kwargs: Additional parameters
        """
        if not api_key or api_key == 'your_fmp_api_key_here':
            raise ValueError("Valid FMP API key is required")
        
        super().__init__(api_key, **kwargs)
        self.base_url = FMP_BASE_URL
        self.rate_limit_per_minute = FMP_RATE_LIMIT_PER_MINUTE
        self.last_request_time = 0
        self.request_count = 0
        self.rate_limit_window_start = time.time()
    
    def _rate_limit(self):
        """Apply rate limiting to API requests."""
        current_time = time.time()
        
        # Reset counter if minute has passed
        if current_time - self.rate_limit_window_start > 60:
            self.request_count = 0
            self.rate_limit_window_start = current_time
        
        # Check if we've hit the rate limit
        if self.request_count >= self.rate_limit_per_minute:
            sleep_time = 60 - (current_time - self.rate_limit_window_start)
            if sleep_time > 0:
                logger.info(f"Rate limit reached, sleeping for {sleep_time:.1f} seconds")
                time.sleep(sleep_time)
                self.request_count = 0
                self.rate_limit_window_start = time.time()
        
        # Minimum delay between requests
        min_delay = 0.1  # 100ms
        time_since_last = current_time - self.last_request_time
        if time_since_last < min_delay:
            time.sleep(min_delay - time_since_last)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make API request with rate limiting and error handling.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
        
        Returns:
            API response as dictionary
        """
        self._rate_limit()
        
        if params is None:
            params = {}
        
        params['apikey'] = self.api_key
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=getattr(self, 'timeout', 30))
            response.raise_for_status()
            
            data = response.json()
            
            # Handle FMP error responses
            if isinstance(data, dict) and data.get('Error Message'):
                raise ValueError(f"FMP API error: {data['Error Message']}")
            
            return data
        
        except Exception as e:
            logger.error(f"FMP API request failed for {endpoint}: {e}")
            raise
    
    def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get basic stock information.
        
        Args:
            symbol: Stock ticker symbol
        
        Returns:
            Dictionary with stock information
        """
        try:
            data = self._make_request(f"profile/{symbol}")
            if isinstance(data, list) and len(data) > 0:
                return data[0]  # type: ignore
            return data if isinstance(data, dict) else {}
        except Exception as e:
            logger.error(f"Failed to get stock info for {symbol}: {e}")
            return {}
    
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
        try:
            params = {
                'from': start_date.strftime('%Y-%m-%d'),
                'to': end_date.strftime('%Y-%m-%d')
            }
            
            data = self._make_request(f"historical-price-full/{symbol}", params)
            
            if not data or 'historical' not in data:
                logger.warning(f"No historical data found for {symbol}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(data['historical'])
            
            if df.empty:
                return df
            
            # Process data
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            df = df.set_index('date')
            
            # Ensure required columns exist
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in required_columns:
                if col not in df.columns:
                    logger.warning(f"Missing column {col} for {symbol}")
                    df[col] = 0.0
            
            # Add adjusted close if not present
            if 'adjClose' in df.columns:
                df['adjusted_close'] = df['adjClose']
            else:
                df['adjusted_close'] = df['close']
            
            return df[['open', 'high', 'low', 'close', 'adjusted_close', 'volume']]
        
        except Exception as e:
            logger.error(f"Failed to get historical prices for {symbol}: {e}")
            return pd.DataFrame()
    
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
        try:
            # Get income statement
            income_endpoint = f"income-statement/{symbol}"
            if period == 'quarterly':
                income_endpoint += "?period=quarter"
            
            income_data = self._make_request(income_endpoint)
            
            # Get balance sheet
            balance_endpoint = f"balance-sheet-statement/{symbol}"
            if period == 'quarterly':
                balance_endpoint += "?period=quarter"
            
            balance_data = self._make_request(balance_endpoint)
            
            # Get key metrics
            metrics_data = self._make_request(f"key-metrics/{symbol}")
            
            # Combine data
            result = {
                'income_statement': income_data if isinstance(income_data, list) else [income_data],
                'balance_sheet': balance_data if isinstance(balance_data, list) else [balance_data],
                'key_metrics': metrics_data if isinstance(metrics_data, list) else [metrics_data]
            }
            
            return result
        
        except Exception as e:
            logger.error(f"Failed to get fundamentals for {symbol}: {e}")
            return {}
    
    def get_stock_list(self) -> List[Dict[str, Any]]:
        """
        Get list of available stocks.
        
        Returns:
            List of dictionaries with stock information
        """
        try:
            # Get list of tradable symbols
            data = self._make_request("stock/list")
            
            if isinstance(data, list):
                # Filter for common stocks and major exchanges
                filtered = []
                for stock in data:
                    if (isinstance(stock, dict) and 
                        stock.get('type') == 'stock' and 
                        stock.get('exchangeShortName') in ['NASDAQ', 'NYSE', 'AMEX']):
                        filtered.append(stock)
                
                return filtered
            
            return []
        
        except Exception as e:
            logger.error(f"Failed to get stock list: {e}")
            return []
    
    def get_sp500_constituents(self) -> List[str]:
        """
        Get S&P 500 constituent symbols.
        
        Returns:
            List of S&P 500 ticker symbols
        """
        try:
            data = self._make_request("sp500_constituent")
            
            if isinstance(data, list):
                return [stock['symbol'] for stock in data if isinstance(stock, dict) and 'symbol' in stock]  # type: ignore
            
            return []
        
        except Exception as e:
            logger.error(f"Failed to get S&P 500 constituents: {e}")
            return []
