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
from reporting.pdf_generator import PDFReportGenerator
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
        self.max_positions = 20
        self.current_positions = set()
        self.metadata = {
            'description': 'Buys stocks above $100, sells below $80',
            'buy_threshold': self.buy_threshold,
            'sell_threshold': self.sell_threshold,
            'max_positions': self.max_positions
        }
    
    def screen_stocks(self, universe: pd.DataFrame, date: pd.Timestamp):
        """Screen for stocks meeting price criteria."""
        # Get stocks with prices in our range
        eligible = universe[
            (universe['close'] > self.sell_threshold)
        ]
        
        # Include current positions (to check for sells)
        all_stocks = set(eligible.index.tolist()) | self.current_positions
        return list(all_stocks)[:self.max_positions * 2]  # Check more than we need
    
    def generate_signals(self, data: pd.Series, date: pd.Timestamp):
        """Generate buy/sell signals based on thresholds."""
        current_price = data.iloc[-1] if len(data) > 0 else 0
        is_holding = data.name in self.current_positions
        
        signal = SignalGenerator.price_threshold(
            data,
            self.buy_threshold,
            self.sell_threshold,
            is_holding
        )
        
        # Update positions tracking
        if signal == 1 and not is_holding:
            self.current_positions.add(data.name)
        elif signal == -1 and is_holding:
            self.current_positions.remove(data.name)
        
        return signal
    
    def allocate_portfolio(self, selected_stocks, signals, current_portfolio, date):
        """Equal weight allocation for buy signals."""
        # Get stocks with buy signals
        buy_stocks = [
            stock for stock in selected_stocks 
            if signals.get(stock, 0) == 1
        ]
        
        # Limit to max positions
        if len(buy_stocks) > self.max_positions:
            buy_stocks = buy_stocks[:self.max_positions]
        
        # Equal weight allocation
        if buy_stocks:
            weights = PortfolioAllocator.equal_weight(buy_stocks)
        else:
            weights = {}
        
        # Set sell signals to 0 weight
        for stock in selected_stocks:
            if signals.get(stock, 0) == -1:
                weights[stock] = 0.0
        
        return weights


def main():
    """Run buy/sell threshold strategy backtest."""
    # Create strategy
    strategy = BuySellThresholdStrategy()
    
    # Create backtest engine
    engine = BacktestEngine(
        strategy=strategy,
        start_date="2022-01-01",
        end_date="2023-12-31",
        universe=None,
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