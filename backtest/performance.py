"""Performance analysis for backtesting."""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PerformanceAnalyzer:
    """Analyzes backtest performance metrics."""
    
    def calculate_metrics(
        self,
        portfolio_values: pd.DataFrame,
        benchmark_data: pd.DataFrame,
        trades: List[Dict],
        initial_capital: float
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive performance metrics.
        
        Args:
            portfolio_values: DataFrame with portfolio values over time
            benchmark_data: DataFrame with benchmark prices
            trades: List of executed trades
            initial_capital: Starting capital
        
        Returns:
            Dictionary with performance metrics
        """
        metrics = {}
        
        # Basic returns
        metrics['total_return'] = self._calculate_total_return(
            portfolio_values, initial_capital
        )
        metrics['annualized_return'] = self._calculate_annualized_return(
            portfolio_values, initial_capital
        )
        
        # Risk metrics
        daily_returns = portfolio_values['value'].pct_change().dropna()
        metrics['volatility'] = self._calculate_volatility(daily_returns)
        metrics['sharpe_ratio'] = self._calculate_sharpe_ratio(
            daily_returns, metrics['annualized_return'], metrics['volatility']
        )
        metrics['max_drawdown'] = self._calculate_max_drawdown(portfolio_values['value'])
        
        # Trading metrics
        metrics['total_trades'] = len(trades)
        metrics['winning_trades'] = self._count_winning_trades(trades)
        metrics['win_rate'] = (
            metrics['winning_trades'] / metrics['total_trades'] 
            if metrics['total_trades'] > 0 else 0
        )
        
        # Benchmark comparison
        if not benchmark_data.empty:
            benchmark_returns = self._calculate_benchmark_returns(
                benchmark_data, 
                portfolio_values.index[0], 
                portfolio_values.index[-1]
            )
            metrics['benchmark_return'] = benchmark_returns['total_return']
            metrics['alpha'] = metrics['annualized_return'] - benchmark_returns['annualized_return']
            metrics['beta'] = self._calculate_beta(daily_returns, benchmark_returns['daily_returns'])
        
        # Additional metrics
        metrics['sortino_ratio'] = self._calculate_sortino_ratio(daily_returns)
        metrics['calmar_ratio'] = self._calculate_calmar_ratio(
            metrics['annualized_return'], 
            metrics['max_drawdown']
        )
        
        return metrics
    
    def _calculate_total_return(
        self, 
        portfolio_values: pd.DataFrame, 
        initial_capital: float
    ) -> float:
        """Calculate total return percentage."""
        final_value = portfolio_values['value'].iloc[-1]
        return (final_value - initial_capital) / initial_capital
    
    def _calculate_annualized_return(
        self, 
        portfolio_values: pd.DataFrame, 
        initial_capital: float
    ) -> float:
        """Calculate annualized return."""
        total_return = self._calculate_total_return(portfolio_values, initial_capital)
        days = len(portfolio_values)
        years = days / 252  # Trading days per year
        
        if years > 0:
            return (1 + total_return) ** (1 / years) - 1
        return 0
    
    def _calculate_volatility(self, daily_returns: pd.Series) -> float:
        """Calculate annualized volatility."""
        return daily_returns.std() * np.sqrt(252)
    
    def _calculate_sharpe_ratio(
        self, 
        daily_returns: pd.Series,
        annualized_return: float,
        volatility: float,
        risk_free_rate: float = 0.05
    ) -> float:
        """Calculate Sharpe ratio."""
        if volatility == 0:
            return 0
        return (annualized_return - risk_free_rate) / volatility
    
    def _calculate_max_drawdown(self, values: pd.Series) -> float:
        """Calculate maximum drawdown."""
        cumulative = (1 + values.pct_change()).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    def _count_winning_trades(self, trades: List[Dict]) -> int:
        """Count number of winning trades."""
        # This is simplified - would need to track buy/sell pairs
        return len([t for t in trades if t['action'] == 'SELL'])
    
    def _calculate_benchmark_returns(
        self, 
        benchmark_data: pd.DataFrame,
        start_date: pd.Timestamp,
        end_date: pd.Timestamp
    ) -> Dict[str, Any]:
        """Calculate benchmark returns."""
        # Get benchmark prices for the period
        benchmark_prices = benchmark_data.xs(
            benchmark_data.index.get_level_values('symbol')[0], 
            level='symbol'
        )['close']
        
        # Filter to backtest period
        benchmark_prices = benchmark_prices[
            (benchmark_prices.index >= start_date) & 
            (benchmark_prices.index <= end_date)
        ]
        
        if benchmark_prices.empty:
            return {'total_return': 0, 'annualized_return': 0, 'daily_returns': pd.Series()}
        
        total_return = (
            benchmark_prices.iloc[-1] - benchmark_prices.iloc[0]
        ) / benchmark_prices.iloc[0]
        
        days = len(benchmark_prices)
        years = days / 252
        annualized_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        
        daily_returns = benchmark_prices.pct_change().dropna()
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'daily_returns': daily_returns
        }
    
    def _calculate_beta(
        self, 
        portfolio_returns: pd.Series, 
        benchmark_returns: pd.Series
    ) -> float:
        """Calculate beta relative to benchmark."""
        if benchmark_returns.empty or portfolio_returns.empty:
            return 1.0
        
        # Align the series
        aligned = pd.DataFrame({
            'portfolio': portfolio_returns,
            'benchmark': benchmark_returns
        }).dropna()
        
        if len(aligned) < 20:  # Need sufficient data
            return 1.0
        
        covariance = aligned['portfolio'].cov(aligned['benchmark'])
        benchmark_variance = aligned['benchmark'].var()
        
        if benchmark_variance == 0:
            return 1.0
        
        return covariance / benchmark_variance
    
    def _calculate_sortino_ratio(
        self, 
        daily_returns: pd.Series,
        target_return: float = 0,
        risk_free_rate: float = 0.05
    ) -> float:
        """Calculate Sortino ratio (uses downside deviation)."""
        excess_returns = daily_returns - risk_free_rate / 252
        downside_returns = excess_returns[excess_returns < target_return]
        
        if len(downside_returns) == 0:
            return 0
        
        downside_deviation = downside_returns.std() * np.sqrt(252)
        
        if downside_deviation == 0:
            return 0
        
        annualized_excess_return = excess_returns.mean() * 252
        return annualized_excess_return / downside_deviation
    
    def _calculate_calmar_ratio(
        self, 
        annualized_return: float, 
        max_drawdown: float
    ) -> float:
        """Calculate Calmar ratio."""
        if max_drawdown == 0:
            return 0
        return annualized_return / abs(max_drawdown)