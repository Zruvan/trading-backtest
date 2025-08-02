"""Database models for trading backtest system."""
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, Boolean,
    ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Stock(Base):
    """Stock information and metadata."""
    __tablename__ = 'stocks'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    sector = Column(String(100))
    industry = Column(String(100))
    market_cap = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    prices = relationship("StockPrice", back_populates="stock")
    fundamentals = relationship("Fundamentals", back_populates="stock")


class StockPrice(Base):
    """Daily stock price data."""
    __tablename__ = 'stock_prices'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    adjusted_close = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    stock = relationship("Stock", back_populates="prices")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('stock_id', 'date', name='unique_stock_date'),
        Index('idx_stock_date', 'stock_id', 'date'),
        Index('idx_date', 'date'),
    )


class Fundamentals(Base):
    """Fundamental data for stocks."""
    __tablename__ = 'fundamentals'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    
    # Financial metrics
    revenue = Column(Float)
    net_income = Column(Float)
    total_assets = Column(Float)
    total_liabilities = Column(Float)
    shareholders_equity = Column(Float)
    
    # Ratios
    pe_ratio = Column(Float)
    pb_ratio = Column(Float)
    debt_to_equity = Column(Float)
    roe = Column(Float)
    roa = Column(Float)
    
    # Per share metrics
    eps = Column(Float)
    book_value_per_share = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    stock = relationship("Stock", back_populates="fundamentals")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('stock_id', 'date', name='unique_fundamental_stock_date'),
        Index('idx_fundamental_stock_date', 'stock_id', 'date'),
    )


class Backtest(Base):
    """Backtest run metadata."""
    __tablename__ = 'backtests'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    strategy_name = Column(String(255), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    initial_capital = Column(Float, nullable=False)
    commission = Column(Float, default=0.001)
    slippage = Column(Float, default=0.0005)
    
    # Performance metrics
    total_return = Column(Float)
    annualized_return = Column(Float)
    volatility = Column(Float)
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)
    
    # Metadata
    parameters = Column(Text)  # JSON string of strategy parameters
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    trades = relationship("Trade", back_populates="backtest")
    portfolio_values = relationship("PortfolioValue", back_populates="backtest")


class Trade(Base):
    """Individual trades executed during backtest."""
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True)
    backtest_id = Column(Integer, ForeignKey('backtests.id'), nullable=False)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    
    date = Column(DateTime, nullable=False)
    action = Column(String(10), nullable=False)  # 'buy' or 'sell'
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    commission = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    backtest = relationship("Backtest", back_populates="trades")
    stock = relationship("Stock")
    
    # Indexes
    __table_args__ = (
        Index('idx_backtest_date', 'backtest_id', 'date'),
        Index('idx_backtest_stock', 'backtest_id', 'stock_id'),
    )


class PortfolioValue(Base):
    """Portfolio value over time during backtest."""
    __tablename__ = 'portfolio_values'
    
    id = Column(Integer, primary_key=True)
    backtest_id = Column(Integer, ForeignKey('backtests.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    total_value = Column(Float, nullable=False)
    cash = Column(Float, nullable=False)
    positions_value = Column(Float, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    backtest = relationship("Backtest", back_populates="portfolio_values")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('backtest_id', 'date', name='unique_portfolio_date'),
        Index('idx_portfolio_backtest_date', 'backtest_id', 'date'),
    )


class CacheEntry(Base):
    """Data cache entries for API responses."""
    __tablename__ = 'cache_entries'
    
    id = Column(Integer, primary_key=True)
    cache_key = Column(String(255), unique=True, nullable=False, index=True)
    data = Column(Text, nullable=False)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_cache_expires', 'expires_at'),
    )
