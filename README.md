# Trading Backtest System

A Python-based backtesting framework for testing trading strategies with comprehensive portfolio analytics and reporting.

## Features

- **Stock Screening**: Market cap, fundamentals, and custom indicators
- **Portfolio Allocation**: Equal weight, market cap weight, and custom strategies  
- **Signal Generation**: Buy/sell signal generation with multiple strategies
- **Performance Analytics**: Comprehensive metrics including Sharpe ratio, maximum drawdown, and risk analysis
- **PDF Reporting**: Professional reports with charts and performance summaries
- **Data Caching**: PostgreSQL/TimescaleDB integration for efficient data storage
- **API Integration**: Financial Modeling Prep API for real-time and historical data

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL with TimescaleDB (optional, can use SQLite for development)
- Financial Modeling Prep API key (get one at [financialmodelingprep.com](https://financialmodelingprep.com))

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Zruvan/trading-backtest.git
   cd trading-backtest
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up configuration:**
   ```bash
   # Copy example files
   cp .env.example .env
   cp config/settings.example.py config/settings.py
   
   # Edit .env file and add your FMP API key
   FMP_API_KEY=your_actual_api_key_here
   ```

5. **Start database (optional - uses SQLite by default):**
   ```bash
   docker-compose up -d
   ```

6. **Initialize database:**
   ```bash
   python scripts/setup_db.py
   ```

7. **Create reports directory:**
   ```bash
   mkdir reports
   ```

8. **Run example strategy:**
   ```bash
   python scripts/examples/market_cap_strategy.py
   ```

## Usage

### Creating a Strategy

All strategies inherit from `BaseStrategy` and implement three core methods:

```python
from strategies.base import BaseStrategy
from strategies.screening import StockScreener
from strategies.allocation import PortfolioAllocator
import pandas as pd

class MyStrategy(BaseStrategy):
    def __init__(self):
        super().__init__(
            name="My Trading Strategy",
            initial_capital=100000,
            rebalance_frequency='monthly'
        )
    
    def screen_stocks(self, universe, date):
        # Select stocks based on your criteria
        return StockScreener.by_market_cap(universe, top_n=20)
    
    def generate_signals(self, data, date):
        # Generate buy/sell signals (1=buy, 0=hold, -1=sell)
        return pd.Series(1, index=data.index)  # Always buy
    
    def allocate_portfolio(self, selected_stocks, signals, current_portfolio, date):
        # Determine position sizes
        return PortfolioAllocator.equal_weight(selected_stocks)
```

### Running a Backtest

```python
from backtest.engine import BacktestEngine
from datetime import datetime

# Initialize strategy
strategy = MyStrategy()

# Create backtest engine
engine = BacktestEngine(strategy)

# Run backtest
results = engine.run(
    start_date=datetime(2020, 1, 1),
    end_date=datetime(2023, 12, 31),
    universe='SP500'  # or list of symbols
)

# Generate report
from reporting.pdf_generator import PDFReportGenerator
report = PDFReportGenerator()
report.generate_report(results, 'my_strategy_report.pdf')
```

## Project Structure

```
trading-backtest/
├── config/              # Configuration files
├── data/                # Data layer (models, database, API connectors)
├── strategies/          # Trading strategies
├── backtest/            # Backtesting engine
├── reporting/           # Report generation
├── scripts/             # Utility scripts and examples
├── tests/               # Test files
└── reports/             # Generated reports (local only)
```

## Built-in Strategies

### Market Cap Strategy
Invests in top N stocks by market capitalization, weighted by market cap.

### Buy/Sell Threshold Strategy
Uses technical indicators to generate buy/sell signals based on price movements and volume.

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Required: Financial Modeling Prep API key
FMP_API_KEY=your_fmp_api_key_here

# Optional: Database configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=trading_backtest
DB_USER=postgres
DB_PASSWORD=password

# Optional: Application settings
DEBUG=True
LOG_LEVEL=INFO
```

### Database Setup

The system supports both SQLite (for development) and PostgreSQL with TimescaleDB (for production):

**SQLite (Default):**
```python
DATABASE_URL = "sqlite:///trading_backtest.db"
```

**PostgreSQL:**
```python
DATABASE_URL = "postgresql://user:password@localhost/trading_backtest"
```

## API Integration

### Financial Modeling Prep

The system uses Financial Modeling Prep API for market data. Key features:

- Historical price data
- Company fundamentals
- Real-time quotes
- Market indices data
- Rate limiting and caching

### Custom Data Sources

Extend `BaseConnector` to add new data sources:

```python
from data.connectors.base import BaseConnector

class MyDataConnector(BaseConnector):
    def get_historical_prices(self, symbol, start_date, end_date):
        # Implement your data source logic
        pass
```

## Performance Metrics

The system calculates comprehensive performance metrics:

- **Returns**: Total, annualized, and period returns
- **Risk Metrics**: Volatility, Sharpe ratio, Sortino ratio
- **Drawdown**: Maximum drawdown, drawdown duration
- **Benchmark Comparison**: Alpha, beta, tracking error
- **Trade Analysis**: Win rate, average trade, profit factor

## Reporting

Generate professional PDF reports with:

- Performance summary
- Risk metrics
- Portfolio composition charts
- Drawdown analysis
- Trade statistics
- Benchmark comparison

## Testing

Run the test suite:

```bash
pytest tests/
```

Run tests with coverage:

```bash
pytest tests/ --cov=. --cov-report=html
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run tests: `pytest`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This software is for educational and research purposes only. It is not intended to provide investment advice. Always consult with a qualified financial advisor before making investment decisions.

## Support

- Create an issue on GitHub for bug reports or feature requests
- Check the documentation in the `docs/` directory
- Review example strategies in `scripts/examples/`

## Roadmap

- [ ] Real-time trading integration
- [ ] Additional data sources (Alpha Vantage, Yahoo Finance)
- [ ] Web-based dashboard
- [ ] Machine learning strategy templates
- [ ] Portfolio optimization tools
- [ ] Risk management features
