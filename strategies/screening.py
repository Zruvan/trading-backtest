"""Stock screening utilities."""
import logging
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class StockScreener:
    """Utilities for screening stocks based on various criteria."""
    
    @staticmethod
    def by_market_cap(
        universe: pd.DataFrame,
        top_n: int = 50,
        ascending: bool = False,
        min_market_cap: float = 1e9
    ) -> List[str]:
        """
        Screen stocks by market capitalization.
        
        Args:
            universe: DataFrame with stock data including 'market_cap' column
            top_n: Number of top stocks to select
            ascending: If True, select smallest market caps
            min_market_cap: Minimum market cap threshold
        
        Returns:
            List of selected stock symbols
        """
        if universe.empty or 'market_cap' not in universe.columns:
            logger.warning("Universe is empty or missing market_cap column")
            return []
        
        # Filter by minimum market cap
        filtered = universe[universe['market_cap'] >= min_market_cap].copy()
        
        if filtered.empty:
            logger.warning("No stocks meet minimum market cap requirement")
            return []
        
        # Sort and select top N
        sorted_stocks = filtered.sort_values('market_cap', ascending=ascending)
        selected = sorted_stocks.head(top_n)
        
        symbols = selected.index.tolist() if hasattr(selected.index, 'tolist') else list(selected.index)
        
        logger.info(f"Selected {len(symbols)} stocks by market cap (ascending={ascending})")
        return symbols
    
    @staticmethod
    def by_volume(
        universe: pd.DataFrame,
        price_data: Dict[str, pd.DataFrame],
        top_n: int = 50,
        min_volume: float = 1e6,
        lookback_days: int = 20
    ) -> List[str]:
        """
        Screen stocks by trading volume.
        
        Args:
            universe: DataFrame with stock data
            price_data: Dictionary mapping symbols to price DataFrames
            top_n: Number of top stocks to select
            min_volume: Minimum average volume threshold
            lookback_days: Number of days to calculate average volume
        
        Returns:
            List of selected stock symbols
        """
        if universe.empty:
            logger.warning("Universe is empty")
            return []
        
        volume_data = []
        symbols = universe.index.tolist() if hasattr(universe.index, 'tolist') else list(universe.index)
        
        for symbol in symbols:
            if symbol not in price_data:
                continue
            
            prices = price_data[symbol]
            if 'volume' not in prices.columns or len(prices) < lookback_days:
                continue
            
            # Calculate average volume over lookback period
            avg_volume = prices['volume'].tail(lookback_days).mean()
            
            if avg_volume >= min_volume:
                volume_data.append({
                    'symbol': symbol,
                    'avg_volume': avg_volume
                })
        
        if not volume_data:
            logger.warning("No stocks meet volume requirements")
            return []
        
        # Sort by volume and select top N
        volume_df = pd.DataFrame(volume_data)
        sorted_stocks = volume_df.sort_values('avg_volume', ascending=False)
        selected_symbols = sorted_stocks.head(top_n)['symbol'].tolist()
        
        logger.info(f"Selected {len(selected_symbols)} stocks by volume")
        return selected_symbols
    
    @staticmethod
    def by_momentum(
        price_data: Dict[str, pd.DataFrame],
        lookback_days: int = 252,
        top_n: int = 50,
        min_periods: int = 100
    ) -> List[str]:
        """
        Screen stocks by price momentum.
        
        Args:
            price_data: Dictionary mapping symbols to price DataFrames
            lookback_days: Number of days for momentum calculation
            top_n: Number of top stocks to select
            min_periods: Minimum number of data points required
        
        Returns:
            List of selected stock symbols
        """
        momentum_data = []
        
        for symbol, prices in price_data.items():
            if 'close' not in prices.columns or len(prices) < min_periods:
                continue
            
            # Calculate momentum as total return over lookback period
            if len(prices) >= lookback_days:
                start_price = prices['close'].iloc[-lookback_days]
                end_price = prices['close'].iloc[-1]
                momentum = (end_price - start_price) / start_price
            else:
                # Use all available data if less than lookback_days
                start_price = prices['close'].iloc[0]
                end_price = prices['close'].iloc[-1]
                momentum = (end_price - start_price) / start_price
            
            momentum_data.append({
                'symbol': symbol,
                'momentum': momentum
            })
        
        if not momentum_data:
            logger.warning("No stocks have sufficient price data for momentum calculation")
            return []
        
        # Sort by momentum and select top N
        momentum_df = pd.DataFrame(momentum_data)
        sorted_stocks = momentum_df.sort_values('momentum', ascending=False)
        selected_symbols = sorted_stocks.head(top_n)['symbol'].tolist()
        
        logger.info(f"Selected {len(selected_symbols)} stocks by momentum")
        return selected_symbols
    
    @staticmethod
    def by_fundamentals(
        universe: pd.DataFrame,
        criteria: Dict[str, Any],
        top_n: Optional[int] = None
    ) -> List[str]:
        """
        Screen stocks by fundamental criteria.
        
        Args:
            universe: DataFrame with fundamental data
            criteria: Dictionary with screening criteria
                     e.g., {'pe_ratio': {'max': 15}, 'debt_to_equity': {'max': 0.5}}
            top_n: Maximum number of stocks to return
        
        Returns:
            List of selected stock symbols
        """
        if universe.empty:
            logger.warning("Universe is empty")
            return []
        
        filtered = universe.copy()
        
        for column, conditions in criteria.items():
            if column not in filtered.columns:
                logger.warning(f"Column {column} not found in universe")
                continue
            
            # Apply min/max filters
            if 'min' in conditions:
                filtered = filtered[filtered[column] >= conditions['min']]
            
            if 'max' in conditions:
                filtered = filtered[filtered[column] <= conditions['max']]
            
            # Remove rows with NaN values in this column
            filtered = filtered.dropna(subset=[column])
        
        if filtered.empty:
            logger.warning("No stocks meet fundamental criteria")
            return []
        
        symbols = filtered.index.tolist() if hasattr(filtered.index, 'tolist') else list(filtered.index)
        
        # Limit to top_n if specified
        if top_n is not None and len(symbols) > top_n:
            symbols = symbols[:top_n]
        
        logger.info(f"Selected {len(symbols)} stocks by fundamental criteria")
        return symbols
    
    @staticmethod
    def by_price_range(
        universe: pd.DataFrame,
        price_data: Dict[str, pd.DataFrame],
        min_price: float = 5.0,
        max_price: float = 1000.0
    ) -> List[str]:
        """
        Screen stocks by current price range.
        
        Args:
            universe: DataFrame with stock data
            price_data: Dictionary mapping symbols to price DataFrames
            min_price: Minimum stock price
            max_price: Maximum stock price
        
        Returns:
            List of selected stock symbols
        """
        if universe.empty:
            logger.warning("Universe is empty")
            return []
        
        selected_symbols = []
        symbols = universe.index.tolist() if hasattr(universe.index, 'tolist') else list(universe.index)
        
        for symbol in symbols:
            if symbol not in price_data:
                continue
            
            prices = price_data[symbol]
            if 'close' not in prices.columns or prices.empty:
                continue
            
            current_price = prices['close'].iloc[-1]
            
            if min_price <= current_price <= max_price:
                selected_symbols.append(symbol)
        
        logger.info(f"Selected {len(selected_symbols)} stocks by price range ${min_price}-${max_price}")
        return selected_symbols
    
    @staticmethod
    def combine_screens(
        screens: List[List[str]],
        method: str = 'intersection'
    ) -> List[str]:
        """
        Combine multiple screening results.
        
        Args:
            screens: List of symbol lists from different screens
            method: 'intersection' (AND) or 'union' (OR)
        
        Returns:
            Combined list of stock symbols
        """
        if not screens:
            return []
        
        if len(screens) == 1:
            return screens[0]
        
        if method == 'intersection':
            # Find symbols that appear in all screens
            result = set(screens[0])
            for screen in screens[1:]:
                result = result.intersection(set(screen))
            symbols = list(result)
        elif method == 'union':
            # Find symbols that appear in any screen
            result = set()
            for screen in screens:
                result = result.union(set(screen))
            symbols = list(result)
        else:
            raise ValueError("Method must be 'intersection' or 'union'")
        
        logger.info(f"Combined {len(screens)} screens using {method}: {len(symbols)} symbols")
        return symbols
