"""Portfolio allocation utilities."""
import logging
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class PortfolioAllocator:
    """Utilities for portfolio allocation strategies."""
    
    @staticmethod
    def equal_weight(symbols: List[str]) -> Dict[str, float]:
        """
        Equal weight allocation across all symbols.
        
        Args:
            symbols: List of stock symbols
        
        Returns:
            Dictionary mapping symbols to weights
        """
        if not symbols:
            return {}
        
        weight = 1.0 / len(symbols)
        allocation = {symbol: weight for symbol in symbols}
        
        logger.debug(f"Equal weight allocation: {len(symbols)} stocks at {weight:.4f} each")
        return allocation
    
    @staticmethod
    def market_cap_weight(
        symbols: List[str],
        universe: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Market capitalization weighted allocation.
        
        Args:
            symbols: List of stock symbols
            universe: DataFrame with market_cap column
        
        Returns:
            Dictionary mapping symbols to weights
        """
        if not symbols or universe.empty or 'market_cap' not in universe.columns:
            logger.warning("Cannot perform market cap weighting: missing data")
            return PortfolioAllocator.equal_weight(symbols)
        
        # Get market caps for selected symbols
        market_caps = {}
        for symbol in symbols:
            if symbol in universe.index:
                market_cap = universe.loc[symbol, 'market_cap']
                if pd.notna(market_cap) and market_cap > 0:
                    market_caps[symbol] = market_cap
        
        if not market_caps:
            logger.warning("No valid market cap data found, using equal weights")
            return PortfolioAllocator.equal_weight(symbols)
        
        # Calculate weights
        total_market_cap = sum(market_caps.values())
        allocation = {symbol: market_cap / total_market_cap 
                     for symbol, market_cap in market_caps.items()}
        
        logger.debug(f"Market cap weighted allocation: {len(allocation)} stocks")
        return allocation
    
    @staticmethod
    def inverse_volatility_weight(
        symbols: List[str],
        price_data: Dict[str, pd.DataFrame],
        lookback_days: int = 252
    ) -> Dict[str, float]:
        """
        Inverse volatility weighted allocation.
        
        Args:
            symbols: List of stock symbols
            price_data: Dictionary mapping symbols to price DataFrames
            lookback_days: Number of days for volatility calculation
        
        Returns:
            Dictionary mapping symbols to weights
        """
        if not symbols:
            return {}
        
        volatilities = {}
        
        for symbol in symbols:
            if symbol not in price_data:
                continue
            
            prices = price_data[symbol]
            if 'close' not in prices.columns or len(prices) < 20:
                continue
            
            # Calculate returns and volatility
            returns = prices['close'].pct_change().dropna()
            if len(returns) < 10:
                continue
            
            # Use specified lookback or all available data
            if len(returns) > lookback_days:
                returns = returns.tail(lookback_days)
            
            volatility = returns.std()
            if volatility > 0:
                volatilities[symbol] = volatility
        
        if not volatilities:
            logger.warning("No valid volatility data found, using equal weights")
            return PortfolioAllocator.equal_weight(symbols)
        
        # Calculate inverse volatility weights
        inverse_vols = {symbol: 1.0 / vol for symbol, vol in volatilities.items()}
        total_inverse_vol = sum(inverse_vols.values())
        
        allocation = {symbol: inv_vol / total_inverse_vol 
                     for symbol, inv_vol in inverse_vols.items()}
        
        logger.debug(f"Inverse volatility weighted allocation: {len(allocation)} stocks")
        return allocation
    
    @staticmethod
    def momentum_weight(
        symbols: List[str],
        price_data: Dict[str, pd.DataFrame],
        lookback_days: int = 63,  # ~3 months
        momentum_power: float = 1.0
    ) -> Dict[str, float]:
        """
        Momentum-based weighted allocation.
        
        Args:
            symbols: List of stock symbols
            price_data: Dictionary mapping symbols to price DataFrames
            lookback_days: Number of days for momentum calculation
            momentum_power: Power to raise momentum scores (>1 increases concentration)
        
        Returns:
            Dictionary mapping symbols to weights
        """
        if not symbols:
            return {}
        
        momentum_scores = {}
        
        for symbol in symbols:
            if symbol not in price_data:
                continue
            
            prices = price_data[symbol]
            if 'close' not in prices.columns or len(prices) < lookback_days:
                continue
            
            # Calculate momentum as total return over lookback period
            start_price = prices['close'].iloc[-lookback_days]
            end_price = prices['close'].iloc[-1]
            
            if start_price > 0:
                momentum = (end_price - start_price) / start_price
                # Only include positive momentum stocks
                if momentum > 0:
                    momentum_scores[symbol] = momentum ** momentum_power
        
        if not momentum_scores:
            logger.warning("No positive momentum stocks found, using equal weights")
            return PortfolioAllocator.equal_weight(symbols)
        
        # Normalize to weights
        total_momentum = sum(momentum_scores.values())
        allocation = {symbol: score / total_momentum 
                     for symbol, score in momentum_scores.items()}
        
        logger.debug(f"Momentum weighted allocation: {len(allocation)} stocks")
        return allocation
    
    @staticmethod
    def target_weight(
        symbols: List[str],
        target_weights: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Use predefined target weights.
        
        Args:
            symbols: List of stock symbols
            target_weights: Dictionary with target weights
        
        Returns:
            Dictionary mapping symbols to weights
        """
        if not symbols:
            return {}
        
        # Extract weights for selected symbols
        allocation = {}
        for symbol in symbols:
            if symbol in target_weights:
                allocation[symbol] = target_weights[symbol]
        
        if not allocation:
            logger.warning("No target weights found for selected symbols, using equal weights")
            return PortfolioAllocator.equal_weight(symbols)
        
        # Normalize weights to sum to 1
        total_weight = sum(allocation.values())
        if total_weight > 0:
            allocation = {symbol: weight / total_weight 
                         for symbol, weight in allocation.items()}
        
        logger.debug(f"Target weighted allocation: {len(allocation)} stocks")
        return allocation
    
    @staticmethod
    def risk_parity(
        symbols: List[str],
        price_data: Dict[str, pd.DataFrame],
        lookback_days: int = 252
    ) -> Dict[str, float]:
        """
        Risk parity allocation (equal risk contribution).
        
        Args:
            symbols: List of stock symbols
            price_data: Dictionary mapping symbols to price DataFrames
            lookback_days: Number of days for covariance calculation
        
        Returns:
            Dictionary mapping symbols to weights
        """
        if not symbols or len(symbols) < 2:
            return PortfolioAllocator.equal_weight(symbols)
        
        # Get returns data
        returns_data = {}
        for symbol in symbols:
            if symbol not in price_data:
                continue
            
            prices = price_data[symbol]
            if 'close' not in prices.columns or len(prices) < 50:
                continue
            
            returns = prices['close'].pct_change().dropna()
            if len(returns) > lookback_days:
                returns = returns.tail(lookback_days)
            
            if len(returns) >= 20:  # Minimum data requirement
                returns_data[symbol] = returns
        
        if len(returns_data) < 2:
            logger.warning("Insufficient data for risk parity, using equal weights")
            return PortfolioAllocator.equal_weight(symbols)
        
        try:
            # Create returns matrix
            returns_df = pd.DataFrame(returns_data)
            returns_df = returns_df.dropna()
            
            if len(returns_df) < 20:
                logger.warning("Insufficient overlapping data for risk parity")
                return PortfolioAllocator.equal_weight(symbols)
            
            # Calculate covariance matrix
            cov_matrix = returns_df.cov()
            
            # Simple risk parity approximation: inverse volatility
            volatilities = returns_df.std()
            inverse_vols = 1.0 / volatilities
            
            # Normalize to weights
            total_inverse_vol = inverse_vols.sum()
            allocation = (inverse_vols / total_inverse_vol).to_dict()
            
            logger.debug(f"Risk parity allocation: {len(allocation)} stocks")
            return allocation
        
        except Exception as e:
            logger.error(f"Error in risk parity calculation: {e}")
            return PortfolioAllocator.equal_weight(symbols)
    
    @staticmethod
    def minimum_variance(
        symbols: List[str],
        price_data: Dict[str, pd.DataFrame],
        lookback_days: int = 252
    ) -> Dict[str, float]:
        """
        Minimum variance portfolio allocation.
        
        Args:
            symbols: List of stock symbols
            price_data: Dictionary mapping symbols to price DataFrames
            lookback_days: Number of days for covariance calculation
        
        Returns:
            Dictionary mapping symbols to weights
        """
        if not symbols or len(symbols) < 2:
            return PortfolioAllocator.equal_weight(symbols)
        
        # Get returns data (similar to risk_parity)
        returns_data = {}
        for symbol in symbols:
            if symbol not in price_data:
                continue
            
            prices = price_data[symbol]
            if 'close' not in prices.columns or len(prices) < 50:
                continue
            
            returns = prices['close'].pct_change().dropna()
            if len(returns) > lookback_days:
                returns = returns.tail(lookback_days)
            
            if len(returns) >= 20:
                returns_data[symbol] = returns
        
        if len(returns_data) < 2:
            logger.warning("Insufficient data for minimum variance, using equal weights")
            return PortfolioAllocator.equal_weight(symbols)
        
        try:
            # Create returns matrix
            returns_df = pd.DataFrame(returns_data)
            returns_df = returns_df.dropna()
            
            if len(returns_df) < 20:
                logger.warning("Insufficient overlapping data for minimum variance")
                return PortfolioAllocator.equal_weight(symbols)
            
            # Calculate covariance matrix
            cov_matrix = returns_df.cov().values
            n_assets = len(cov_matrix)
            
            # Simple minimum variance: inverse of diagonal (individual variances)
            # This is a simplified approach - full optimization would require quadratic programming
            variances = np.diag(cov_matrix)
            inverse_vars = 1.0 / variances
            
            # Normalize to weights
            weights = inverse_vars / np.sum(inverse_vars)
            
            # Convert back to dictionary
            allocation = dict(zip(returns_df.columns, weights))
            
            logger.debug(f"Minimum variance allocation: {len(allocation)} stocks")
            return allocation
        
        except Exception as e:
            logger.error(f"Error in minimum variance calculation: {e}")
            return PortfolioAllocator.equal_weight(symbols)
    
    @staticmethod
    def validate_allocation(allocation: Dict[str, float]) -> Dict[str, float]:
        """
        Validate and normalize allocation weights.
        
        Args:
            allocation: Dictionary with allocation weights
        
        Returns:
            Validated and normalized allocation
        """
        if not allocation:
            return {}
        
        # Remove zero or negative weights
        valid_allocation = {symbol: weight for symbol, weight in allocation.items() 
                          if weight > 0 and pd.notna(weight)}
        
        if not valid_allocation:
            return {}
        
        # Normalize to sum to 1
        total_weight = sum(valid_allocation.values())
        if total_weight > 0:
            valid_allocation = {symbol: weight / total_weight 
                              for symbol, weight in valid_allocation.items()}
        
        return valid_allocation
