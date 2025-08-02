"""Base strategy class for all trading strategies."""
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseStrategy(ABC):
    """Base class for all trading strategies."""
    
    def __init__(
        self,
        name: str,
        initial_capital: float = 100000,
        rebalance_frequency: str = 'monthly',
        commission: float = 0.001,
        slippage: float = 0.0005,
        **kwargs
    ):
        """
        Initialize strategy.
        
        Args:
            name: Strategy name
            initial_capital: Initial portfolio capital
            rebalance_frequency: How often to rebalance ('daily', 'weekly', 'monthly', 'quarterly')
            commission: Commission rate (as decimal, e.g., 0.001 for 0.1%)
            slippage: Slippage rate (as decimal)
            **kwargs: Additional strategy-specific parameters
        """
        self.name = name
        self.initial_capital = initial_capital
        self.rebalance_frequency = rebalance_frequency
        self.commission = commission
        self.slippage = slippage
        
        # Strategy-specific parameters
        self.parameters = kwargs
        
        # Metadata for reporting
        self.metadata = {
            'description': '',
            'universe': '',
            'rebalance': rebalance_frequency,
            'parameters': kwargs
        }
        
        # Internal state
        self._price_data = {}
        self._fundamental_data = {}
        self._universe = pd.DataFrame()
        
        logger.info(f"Initialized strategy: {name}")
    
    @abstractmethod
    def screen_stocks(self, universe: pd.DataFrame, date: pd.Timestamp) -> List[str]:
        """
        Screen stocks from universe based on strategy criteria.
        
        Args:
            universe: DataFrame with available stocks and their data
            date: Current date for screening
        
        Returns:
            List of selected stock symbols
        """
        pass
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame, date: pd.Timestamp) -> pd.Series:
        """
        Generate buy/sell signals for selected stocks.
        
        Args:
            data: DataFrame with stock data for selected stocks
            date: Current date for signal generation
        
        Returns:
            Series with signals (1 for buy, 0 for hold, -1 for sell)
        """
        pass
    
    @abstractmethod
    def allocate_portfolio(
        self,
        selected_stocks: List[str],
        signals: pd.Series,
        current_portfolio: Dict[str, float],
        date: pd.Timestamp
    ) -> Dict[str, float]:
        """
        Allocate portfolio weights for selected stocks.
        
        Args:
            selected_stocks: List of selected stock symbols
            signals: Buy/sell signals for stocks
            current_portfolio: Current portfolio weights
            date: Current date for allocation
        
        Returns:
            Dictionary mapping stock symbols to target weights
        """
        pass
    
    def set_price_data(self, price_data: Dict[str, pd.DataFrame]):
        """
        Set price data for the strategy.
        
        Args:
            price_data: Dictionary mapping symbols to price DataFrames
        """
        self._price_data = price_data
        logger.debug(f"Set price data for {len(price_data)} symbols")
    
    def set_fundamental_data(self, fundamental_data: Dict[str, Any]):
        """
        Set fundamental data for the strategy.
        
        Args:
            fundamental_data: Dictionary with fundamental data
        """
        self._fundamental_data = fundamental_data
        logger.debug("Set fundamental data")
    
    def set_universe(self, universe: pd.DataFrame):
        """
        Set stock universe for the strategy.
        
        Args:
            universe: DataFrame with stock universe data
        """
        self._universe = universe
        logger.debug(f"Set universe with {len(universe)} stocks")
    
    def get_price_data(self, symbol: str, date: Optional[pd.Timestamp] = None) -> pd.DataFrame:
        """
        Get price data for a symbol up to a specific date.
        
        Args:
            symbol: Stock symbol
            date: End date (if None, returns all data)
        
        Returns:
            DataFrame with price data
        """
        if symbol not in self._price_data:
            logger.warning(f"No price data available for {symbol}")
            return pd.DataFrame()
        
        data = self._price_data[symbol].copy()
        
        if date is not None:
            data = data[data.index <= date]
        
        return data
    
    def get_returns(self, symbol: str, periods: int = 1, date: Optional[pd.Timestamp] = None) -> float:
        """
        Calculate returns for a symbol.
        
        Args:
            symbol: Stock symbol
            periods: Number of periods for return calculation
            date: End date for calculation
        
        Returns:
            Return as decimal (e.g., 0.1 for 10%)
        """
        data = self.get_price_data(symbol, date)
        
        if len(data) < periods + 1:
            return 0.0
        
        try:
            current_price = data['close'].iloc[-1]
            past_price = data['close'].iloc[-(periods + 1)]
            return (current_price - past_price) / past_price
        except (IndexError, ZeroDivisionError):
            return 0.0
    
    def get_volatility(self, symbol: str, window: int = 30, date: Optional[pd.Timestamp] = None) -> float:
        """
        Calculate volatility for a symbol.
        
        Args:
            symbol: Stock symbol
            window: Number of periods for volatility calculation
            date: End date for calculation
        
        Returns:
            Annualized volatility
        """
        data = self.get_price_data(symbol, date)
        
        if len(data) < window:
            return 0.0
        
        try:
            returns = data['close'].pct_change().dropna()
            if len(returns) < 2:
                return 0.0
            
            # Annualized volatility
            return returns.std() * (252 ** 0.5)
        except Exception:
            return 0.0
    
    def validate_allocation(self, allocation: Dict[str, float]) -> Dict[str, float]:
        """
        Validate and normalize portfolio allocation.
        
        Args:
            allocation: Dictionary with stock allocations
        
        Returns:
            Normalized allocation dictionary
        """
        if not allocation:
            return {}
        
        # Remove zero or negative allocations
        allocation = {k: v for k, v in allocation.items() if v > 0}
        
        # Normalize to sum to 1
        total = sum(allocation.values())
        if total > 0:
            allocation = {k: v / total for k, v in allocation.items()}
        
        return allocation
    
    def get_parameter(self, name: str, default: Any = None) -> Any:
        """
        Get strategy parameter value.
        
        Args:
            name: Parameter name
            default: Default value if parameter not found
        
        Returns:
            Parameter value
        """
        return self.parameters.get(name, default)
    
    def set_parameter(self, name: str, value: Any):
        """
        Set strategy parameter value.
        
        Args:
            name: Parameter name
            value: Parameter value
        """
        self.parameters[name] = value
    
    def __str__(self) -> str:
        """String representation of strategy."""
        return f"{self.name} (Capital: ${self.initial_capital:,.0f}, Rebalance: {self.rebalance_frequency})"
    
    def __repr__(self) -> str:
        """Detailed representation of strategy."""
        return (f"BaseStrategy(name='{self.name}', "
                f"initial_capital={self.initial_capital}, "
                f"rebalance_frequency='{self.rebalance_frequency}')")
