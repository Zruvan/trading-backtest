"""Basic tests for trading backtest system."""

import unittest
import sys
import os
from datetime import datetime
from typing import Dict, List
import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backtest.engine import BacktestEngine
from strategies.base import BaseStrategy
from data.database import DatabaseManager
from config import settings


class TestStrategy(BaseStrategy):
    """Test strategy implementation for testing purposes."""
    
    def screen_stocks(self, universe: pd.DataFrame, date: pd.Timestamp) -> List[str]:
        """Return a simple list of stocks for testing."""
        return ['AAPL', 'MSFT', 'GOOGL']
    
    def generate_signals(self, data: pd.DataFrame, date: pd.Timestamp) -> pd.Series:
        """Generate simple buy signals for testing."""
        return pd.Series(1.0, index=data.index if not data.empty else ['AAPL', 'MSFT', 'GOOGL'])
    
    def allocate_portfolio(
        self,
        selected_stocks: List[str],
        signals: pd.Series,
        current_portfolio: Dict[str, float],
        date: pd.Timestamp
    ) -> Dict[str, float]:
        """Equal weight allocation for testing."""
        if not selected_stocks:
            return {}
        weight = 1.0 / len(selected_stocks)
        return {stock: weight for stock in selected_stocks}


class TestBasicImports(unittest.TestCase):
    """Test that all basic modules can be imported."""
    
    def test_backtest_engine_import(self):
        """Test backtest engine import."""
        self.assertIsNotNone(BacktestEngine)
    
    def test_base_strategy_import(self):
        """Test base strategy import."""
        self.assertIsNotNone(BaseStrategy)
    
    def test_database_manager_import(self):
        """Test database manager import."""
        self.assertIsNotNone(DatabaseManager)
    
    def test_settings_import(self):
        """Test settings import."""
        self.assertIsNotNone(settings)


class TestBaseStrategy(unittest.TestCase):
    """Test base strategy functionality."""
    
    def setUp(self):
        """Set up test strategy."""
        self.strategy = TestStrategy(
            name="Test Strategy",
            initial_capital=100000
        )
    
    def test_strategy_initialization(self):
        """Test strategy initialization."""
        self.assertEqual(self.strategy.name, "Test Strategy")
        self.assertEqual(self.strategy.initial_capital, 100000)
        self.assertIsNotNone(self.strategy.metadata)
    
    def test_strategy_has_required_methods(self):
        """Test that strategy has required methods."""
        self.assertTrue(hasattr(self.strategy, 'screen_stocks'))
        self.assertTrue(hasattr(self.strategy, 'generate_signals'))
        self.assertTrue(hasattr(self.strategy, 'allocate_portfolio'))
    
    def test_strategy_methods_work(self):
        """Test that strategy methods return expected types."""
        # Test screen_stocks
        universe = pd.DataFrame()
        date = pd.Timestamp.now()
        stocks = self.strategy.screen_stocks(universe, date)
        self.assertIsInstance(stocks, list)
        
        # Test generate_signals
        data = pd.DataFrame()
        signals = self.strategy.generate_signals(data, date)
        self.assertIsInstance(signals, pd.Series)
        
        # Test allocate_portfolio
        allocation = self.strategy.allocate_portfolio(['AAPL'], signals, {}, date)
        self.assertIsInstance(allocation, dict)


class TestBacktestEngine(unittest.TestCase):
    """Test backtest engine functionality."""
    
    def setUp(self):
        """Set up test engine."""
        strategy = TestStrategy(
            name="Test Strategy",
            initial_capital=100000
        )
        self.engine = BacktestEngine(strategy)
    
    def test_engine_initialization(self):
        """Test engine initialization."""
        self.assertIsNotNone(self.engine.strategy)
        self.assertEqual(self.engine.cash, 100000)
        self.assertEqual(len(self.engine.portfolio), 0)
        self.assertEqual(len(self.engine.trades), 0)
    
    def test_engine_has_required_methods(self):
        """Test that engine has required methods."""
        self.assertTrue(hasattr(self.engine, 'run'))
        self.assertTrue(hasattr(self.engine, 'performance_analyzer'))


if __name__ == '__main__':
    unittest.main()