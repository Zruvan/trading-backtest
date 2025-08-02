"""Example: Market Cap Weighted Strategy"""
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
from reporting.pdf_generator import PDFReportGenerator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketCapStrategy(BaseStrategy):
    """
    Strategy that:
    1. Selects top 10 stocks by market cap
    2. Weights them by market cap
    3. Rebalances monthly
    """
    
    def __init__(self):
        super().__init__(
            name="Market Cap Top 10 Strategy",
            initial_capital=100000,
            rebalance_frequency='monthly',
            commission=0.001,
            slippage=0.0005
        )
        self.top_n = 10
        self.metadata = {
            'description': 'Invests in top 10 stocks by market cap, weighted by market cap',
            'universe': 'S&P 500 constituents',
            'rebalance': 'Monthly'
        }
    
    def screen_stocks(self, universe: pd.DataFrame, date: pd.Timestamp):
        """Select top 10 stocks by market cap."""
        return StockScreener.by_market_cap(universe, top_n=self.top_n, ascending=False)
    
    def generate_signals(self, data: pd.DataFrame, date: pd.Timestamp):
        """Always buy signal for selected stocks."""
        # Simple strategy - always hold selected stocks
        return pd.Series(1, index=data.index)
    
    def allocate_portfolio(self, selected_stocks, signals, current_portfolio, date):
        """Allocate by market cap weight."""
        # Create a simple universe DataFrame with market caps for testing
        import pandas as pd
        
        # Mock market cap data for selected stocks
        mock_market_caps = {
            stock: 1000000000 * (len(selected_stocks) - i)  # Decreasing market caps
            for i, stock in enumerate(selected_stocks)
        }
        
        # Create a DataFrame with market cap data
        universe_df = pd.DataFrame({
            'market_cap': mock_market_caps
        })
        
        return PortfolioAllocator.market_cap_weight(
            selected_stocks, 
            universe_df
        )
def main():
    """Run market cap strategy backtest."""
    from datetime import datetime
    import os
    
    # Create strategy
    strategy = MarketCapStrategy()
    
    # Create backtest engine
    engine = BacktestEngine(strategy)
    
    # Run backtest
    logger.info("Running backtest...")
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2023, 12, 31)
    
    results = engine.run(
        start_date=start_date,
        end_date=end_date,
        universe=['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'JNJ', 'PG'],
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
    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    main()