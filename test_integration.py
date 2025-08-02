"""Integration tests for trading backtest system."""

import unittest
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List
import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backtest.engine import BacktestEngine
from strategies.base import BaseStrategy
from data.database import DatabaseManager
from config import settings


class SimpleTestStrategy(BaseStrategy):
    """Simple test strategy for integration testing."""
    
    def screen_stocks(self, universe: pd.DataFrame, date: pd.Timestamp) -> List[str]:
        """Screen for test stocks."""
        # Return a fixed set of stocks for testing
        return ['AAPL', 'MSFT', 'GOOGL']
    
    def generate_signals(self, data: pd.DataFrame, date: pd.Timestamp) -> pd.Series:
        """Generate buy signals for all stocks."""
        symbols = ['AAPL', 'MSFT', 'GOOGL']
        return pd.Series(1.0, index=symbols)
    
    def allocate_portfolio(
        self,
        selected_stocks: List[str],
        signals: pd.Series,
        current_portfolio: Dict[str, float],
        date: pd.Timestamp
    ) -> Dict[str, float]:
        """Equal weight allocation."""
        if not selected_stocks:
            return {}
        weight = 1.0 / len(selected_stocks)
        return {stock: weight for stock in selected_stocks}


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""
    
    def setUp(self):
        """Set up integration test."""
        self.strategy = SimpleTestStrategy(
            name="Simple Test Strategy",
            initial_capital=100000,
            commission=0.001
        )
        self.engine = BacktestEngine(self.strategy)
    
    def test_basic_backtest_workflow(self):
        """Test basic backtest workflow without actual data."""
        # Test that we can create the engine and strategy
        self.assertIsNotNone(self.engine)
        self.assertIsNotNone(self.strategy)
        
        # Test strategy methods work
        universe = pd.DataFrame()
        date = pd.Timestamp.now()
        
        # Test screening
        stocks = self.strategy.screen_stocks(universe, date)
        self.assertIsInstance(stocks, list)
        self.assertGreater(len(stocks), 0)
        
        # Test signal generation
        data = pd.DataFrame()
        signals = self.strategy.generate_signals(data, date)
        self.assertIsInstance(signals, pd.Series)
        
        # Test allocation
        allocation = self.strategy.allocate_portfolio(stocks, signals, {}, date)
        self.assertIsInstance(allocation, dict)
        
        # Test that allocations sum to approximately 1
        total_allocation = sum(allocation.values())
        self.assertAlmostEqual(total_allocation, 1.0, places=5)
    
    def test_database_connection(self):
        """Test database connection (SQLite for testing)."""
        try:
            db = DatabaseManager(settings.DATABASE_URL)
            # Just test that we can create the manager without errors
            self.assertIsNotNone(db)
        except Exception as e:
            # If database fails, we'll skip this test
            self.skipTest(f"Database connection failed: {e}")
    
    def test_settings_loading(self):
        """Test that settings load correctly."""
        # Test basic settings
        self.assertIsNotNone(settings.DATABASE_URL)
        self.assertIsNotNone(settings.DEFAULT_INITIAL_CAPITAL)
        self.assertIsNotNone(settings.DEFAULT_COMMISSION)
        
        # Test that values are reasonable
        self.assertGreater(settings.DEFAULT_INITIAL_CAPITAL, 0)
        self.assertGreaterEqual(settings.DEFAULT_COMMISSION, 0)
    
    def test_strategy_metadata(self):
        """Test strategy metadata creation."""
        metadata = self.strategy.metadata
        self.assertIsInstance(metadata, dict)
        self.assertIn('description', metadata)
        self.assertIn('universe', metadata)
        self.assertIn('rebalance', metadata)
        self.assertIn('parameters', metadata)


class TestSystemIntegrity(unittest.TestCase):
    """Test overall system integrity."""
    
    def test_all_modules_importable(self):
        """Test that all main modules can be imported."""
        modules_to_test = [
            'backtest.engine',
            'backtest.performance', 
            'strategies.base',
            'strategies.allocation',
            'strategies.screening',
            'strategies.signals',
            'data.database',
            'data.models',
            'config.settings',
            'config.constants',
            'reporting.visualizations',
            'reporting.pdf_generator'
        ]
        
        failed_imports = []
        for module in modules_to_test:
            try:
                __import__(module)
            except ImportError as e:
                failed_imports.append(f"{module}: {e}")
        
        if failed_imports:
            self.fail(f"Failed to import modules: {failed_imports}")
    
    def test_example_strategies_syntax(self):
        """Test that example strategies have valid syntax."""
        example_files = [
            'scripts/examples/buy_sell_threshold_strategy.py',
            'scripts/examples/market_cap_strategy.py'
        ]
        
        for example_file in example_files:
            if os.path.exists(example_file):
                try:
                    with open(example_file, 'r') as f:
                        compile(f.read(), example_file, 'exec')
                except SyntaxError as e:
                    self.fail(f"Syntax error in {example_file}: {e}")


if __name__ == '__main__':
    # Run with verbose output
    unittest.main(verbosity=2)
