"""Example: Buy/Sell Threshold Strategy"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
import pandas as pd
from strategies.base import BaseStrategy
from strategies.screening import StockScreener
from strategies.allocation import PortfolioAllocator
from strategies.signals import SignalGenerator
from backtest.engine import BacktestEngine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BuySellThresholdStrategy(BaseStrategy):
    """
    Strategy that:
    1. Buys when price is above $100
    2. Sells when price falls below $80
    3. Equal weights positions
    """
    
    def __init__(self):
        super().__init__(
            name="Buy/Sell Threshold Strategy",
            initial_capital=100000,
            rebalance_frequency='daily',
            commission=0.001,
            slippage=0.0005
        )
        self.buy_threshold = 100
        self.sell_threshold = 80
        self.max_positions = 5
        self.metadata = {
            'description': 'Buys stocks above $100, sells below $80',
            'buy_threshold': self.buy_threshold,
            'sell_threshold': self.sell_threshold,
            'max_positions': self.max_positions
        }
    
    def screen_stocks(self, universe: pd.DataFrame, date: pd.Timestamp):
        """Screen for stocks meeting price criteria."""
        # For this example, return a fixed list of stocks
        # In a real implementation, this would filter based on actual price data
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'][:self.max_positions]
    
    def generate_signals(self, data: pd.DataFrame, date: pd.Timestamp):
        """Generate buy/sell signals based on thresholds."""
        # For this simplified example, generate buy signals for all stocks
        # In a real implementation, this would check actual price thresholds
        return pd.Series(1, index=data.index)
    
    def allocate_portfolio(self, selected_stocks, signals, current_portfolio, date):
        """Equal weight allocation for selected stocks."""
        # Get stocks with buy signals
        buy_stocks = [
            stock for stock in selected_stocks 
            if signals.get(stock, 0) == 1
        ]
        
        # Limit to max positions
        if len(buy_stocks) > self.max_positions:
            buy_stocks = buy_stocks[:self.max_positions]
        
        # Equal weight allocation
        return PortfolioAllocator.equal_weight(buy_stocks) if buy_stocks else {}


def main():
    """Run buy/sell threshold strategy backtest."""
    from datetime import datetime
    import os
    
    # Create strategy
    strategy = BuySellThresholdStrategy()
    
    # Create backtest engine
    engine = BacktestEngine(strategy)
    
    # Run backtest
    logger.info("Running backtest...")
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2023, 12, 31)
    
    results = engine.run(
        start_date=start_date,
        end_date=end_date,
        universe=['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'],
        benchmark="SPY"
    )
    
    # Print summary
    print("\n=== Backtest Results Summary ===")
    print(f"Strategy: {results['strategy_name']}")
    print(f"Period: {results['start_date'].strftime('%Y-%m-%d')} to {results['end_date'].strftime('%Y-%m-%d')}")
    print(f"Initial Capital: ${results['initial_capital']:,.2f}")
    print(f"Final Value: ${results['final_value']:,.2f}")
    print(f"Total Return: {results['total_return']*100:.2f}%")
    print(f"Annualized Return: {results['annualized_return']*100:.2f}%")
    print(f"Sharpe Ratio: {results['sharpe_ratio']:.3f}")
    print(f"Max Drawdown: {results['max_drawdown']*100:.2f}%")
    print(f"Volatility: {results['volatility']*100:.2f}%")
    
    logger.info("Backtest completed successfully!")
    return results


if __name__ == "__main__":
    main()