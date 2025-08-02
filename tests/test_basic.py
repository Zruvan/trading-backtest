"""Basic tests for the trading backtest system."""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from strategies.screening import StockScreener
from strategies.allocation import PortfolioAllocator
from strategies.signals import SignalGenerator
from backtest.portfolio import Portfolio


class TestScreening:
    """Test stock screening functions."""
    
    def test_market_cap_screening(self):
        """Test market cap based screening."""
        # Create test data
        universe = pd.DataFrame({
            'market_cap': [1000, 2000, 500, 3000, 1500]
        }, index=['A', 'B', 'C', 'D', 'E'])
        
        # Test top 3 by market cap
        result = StockScreener.by_market_cap(universe, top_n=3)
        assert result == ['D', 'B', 'E']
        
        # Test bottom 2 by market cap
        result = StockScreener.by_market_cap(universe, top_n=2, ascending=True)
        assert result == ['C', 'A']


class TestAllocation:
    """Test portfolio allocation functions."""
    
    def test_equal_weight(self):
        """Test equal weight allocation."""
        symbols = ['A', 'B', 'C', 'D']
        weights = PortfolioAllocator.equal_weight(symbols)
        
        assert len(weights) == 4
        assert all(w == 0.25 for w in weights.values())
        assert sum(weights.values()) == 1.0
    
    def test_market_cap_weight(self):
        """Test market cap weighted allocation."""
        symbols = ['A', 'B', 'C']
        market_caps = pd.Series([1000, 2000, 3000], index=symbols)
        
        weights = PortfolioAllocator.market_cap_weight(symbols, market_caps)
        
        assert weights['A'] == pytest.approx(1/6)
        assert weights['B'] == pytest.approx(2/6)
        assert weights['C'] == pytest.approx(3/6)
        assert sum(weights.values()) == pytest.approx(1.0)


class TestSignals:
    """Test signal generation functions."""
    
    def test_price_threshold_signal(self):
        """Test price threshold signals."""
        prices = pd.Series([90, 95, 101, 105, 98, 79])
        
        # Test buy signal
        signal = SignalGenerator.price_threshold(prices, 100, 80, False)
        assert signal == 1  # Current price 79 < 100, but we're not holding
        
        # Test sell signal
        signal = SignalGenerator.price_threshold(prices, 100, 80, True)
        assert signal == -1  # Current price 79 < 80 and we're holding


class TestPortfolio:
    """Test portfolio management."""
    
    def test_portfolio_initialization(self):
        """Test portfolio initialization."""
        portfolio = Portfolio(100000)
        
        assert portfolio.cash == 100000
        assert portfolio.get_value() == 100000
        assert len(portfolio.positions) == 0
    
    def test_portfolio_value(self):
        """Test portfolio value calculation."""
        portfolio = Portfolio(100000)
        
        # Add some positions manually
        portfolio.positions = {'AAPL': 100, 'GOOGL': 50}
        portfolio.current_prices = {'AAPL': 150, 'GOOGL': 2000}
        
        assert portfolio.get_positions_value() == 100 * 150 + 50 * 2000
        assert portfolio.get_value() == 100000 + 100 * 150 + 50 * 2000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])