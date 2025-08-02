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
        # Get market caps for selected stocks
        market_caps = pd.Series()
        for stock in selected_stocks:
            # This would come from fundamental data in real implementation
            market_caps[stock] = 1.0  # Placeholder
        
        return PortfolioAllocator.market_cap_weight(
            selected_stocks, 
            market_caps,
            max_weight=0.20  # Max 20% per position
        )


def main():
    """Run market cap strategy backtest."""
    # Create strategy
    strategy = MarketCapStrategy()
    
    # Create backtest engine
    engine = BacktestEngine(
        strategy=strategy,
        start_date="2022-01-01",
        end_date="2023-12-31",
        universe=None,  # Will use available stocks
        benchmark="SPY"
    )
    
    # Load data
    logger.info("Loading market data...")
    engine.load_data()
    
    # Run backtest
    logger.info("Running backtest...")
    results = engine.run()
    
    # Generate report
    logger.info("Generating report...")
    report_path = f"reports/{strategy.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    os.makedirs("reports", exist_ok=True)
    
    report_generator = PDFReportGenerator(results, report_path)
    report_generator.generate_report()
    
    # Print summary
    print("\n=== Backtest Results Summary ===")
    print(f"Total Return: {results['total_return']*100:.2f}%")
    print(f"Annualized Return: {results['annualized_return']*100:.2f}%")
    print(f"Sharpe Ratio: {results['sharpe_ratio']:.3f}")
    print(f"Max Drawdown: {results['max_drawdown']*100:.2f}%")
    print(f"Total Trades: {results['total_trades']}")
    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    main()