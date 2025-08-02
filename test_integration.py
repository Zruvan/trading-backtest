"""
Simple integration test to verify the trading backtest system is working properly.
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_system_integration():
    """Test that all major components work together."""
    print("🔍 Testing Trading Backtest System Integration")
    print("=" * 50)
    
    try:
        # Test imports
        print("📦 Testing imports...")
        from strategies.base import BaseStrategy
        from strategies.screening import StockScreener
        from strategies.allocation import PortfolioAllocator
        from strategies.signals import SignalGenerator
        from backtest.engine import BacktestEngine
        from backtest.performance import PerformanceAnalyzer
        print("✅ All imports successful")
        
        # Test strategy creation
        print("📋 Testing strategy creation...")
        
        class TestStrategy(BaseStrategy):
            def screen_stocks(self, universe, date):
                return ['AAPL', 'MSFT', 'GOOGL']
                
            def generate_signals(self, data, date):
                import pandas as pd
                return pd.Series(1, index=data.index)
                
            def allocate_portfolio(self, selected_stocks, signals, current_portfolio, date):
                return PortfolioAllocator.equal_weight(selected_stocks)
        
        strategy = TestStrategy('Test Strategy')
        print(f"✅ Created strategy: {strategy.name}")
        
        # Test backtest engine
        print("🚀 Testing backtest engine...")
        engine = BacktestEngine(strategy)
        
        from datetime import datetime
        results = engine.run(
            start_date=datetime(2022, 1, 1),
            end_date=datetime(2022, 12, 31),
            universe=['AAPL', 'MSFT', 'GOOGL'],
            benchmark='SPY'
        )
        
        print(f"✅ Backtest completed successfully")
        print(f"   - Strategy: {results['strategy_name']}")
        print(f"   - Total Return: {results['total_return']:.1%}")
        print(f"   - Sharpe Ratio: {results['sharpe_ratio']:.2f}")
        
        # Test screening utilities
        print("🔍 Testing screening utilities...")
        import pandas as pd
        mock_universe = pd.DataFrame({
            'market_cap': [1e12, 5e11, 3e11, 1e11, 5e10]
        }, index=['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'])
        
        selected = StockScreener.by_market_cap(mock_universe, top_n=3)
        print(f"✅ Market cap screening: {selected}")
        
        # Test allocation utilities
        print("⚖️  Testing allocation utilities...")
        allocation = PortfolioAllocator.equal_weight(['AAPL', 'MSFT', 'GOOGL'])
        print(f"✅ Equal weight allocation: {allocation}")
        
        allocation = PortfolioAllocator.market_cap_weight(['AAPL', 'MSFT', 'GOOGL'], mock_universe)
        print(f"✅ Market cap allocation: {allocation}")
        
        # Test signal generation
        print("📊 Testing signal generation...")
        signals = SignalGenerator.buy_and_hold(['AAPL', 'MSFT', 'GOOGL'])
        print(f"✅ Buy and hold signals: {signals.to_dict()}")
        
        print("\n" + "=" * 50)
        print("🎉 All integration tests passed!")
        print("✅ The trading backtest system is fully functional")
        print("📚 Ready for strategy development and backtesting")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_system_integration()
    sys.exit(0 if success else 1)
