"""Visualization utilities for backtest reports."""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


class BacktestVisualizer:
    """Creates visualizations for backtest results."""
    
    def __init__(self, figsize: Tuple[int, int] = (12, 8)):
        """Initialize visualizer with default figure size."""
        self.figsize = figsize
    
    def plot_portfolio_value(
        self, 
        portfolio_values: pd.DataFrame,
        benchmark_values: Optional[pd.Series] = None,
        title: str = "Portfolio Value Over Time"
    ) -> plt.Figure:
        """Plot portfolio value over time."""
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Plot portfolio value
        ax.plot(
            portfolio_values.index, 
            portfolio_values['value'], 
            label='Portfolio', 
            linewidth=2
        )
        
        # Plot benchmark if provided
        if benchmark_values is not None:
            # Normalize benchmark to start at same value as portfolio
            initial_portfolio = portfolio_values['value'].iloc[0]
            initial_benchmark = benchmark_values.iloc[0]
            normalized_benchmark = benchmark_values * (initial_portfolio / initial_benchmark)
            
            ax.plot(
                normalized_benchmark.index,
                normalized_benchmark.values,
                label='Benchmark',
                linewidth=2,
                alpha=0.7
            )
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Portfolio Value ($)', fontsize=12)
        ax.legend(loc='upper left', fontsize=10)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.xticks(rotation=45)
        
        # Add grid
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def plot_returns_distribution(
        self, 
        returns: pd.Series,
        title: str = "Returns Distribution"
    ) -> plt.Figure:
        """Plot distribution of returns."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(self.figsize[0], self.figsize[1]//2))
        
        # Histogram
        ax1.hist(returns.dropna(), bins=50, alpha=0.7, edgecolor='black')
        ax1.axvline(returns.mean(), color='red', linestyle='--', label=f'Mean: {returns.mean():.2%}')
        ax1.axvline(returns.median(), color='green', linestyle='--', label=f'Median: {returns.median():.2%}')
        ax1.set_title('Returns Histogram', fontsize=14)
        ax1.set_xlabel('Daily Returns', fontsize=12)
        ax1.set_ylabel('Frequency', fontsize=12)
        ax1.legend()
        
        # Q-Q plot
        from scipy import stats
        stats.probplot(returns.dropna(), dist="norm", plot=ax2)
        ax2.set_title('Q-Q Plot', fontsize=14)
        ax2.grid(True, alpha=0.3)
        
        plt.suptitle(title, fontsize=16, fontweight='bold')
        plt.tight_layout()
        return fig
    
    def plot_drawdown(
        self, 
        portfolio_values: pd.DataFrame,
        title: str = "Portfolio Drawdown"
    ) -> plt.Figure:
        """Plot drawdown over time."""
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Calculate drawdown
        cumulative = portfolio_values['value']
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max * 100
        
        # Plot drawdown
        ax.fill_between(
            drawdown.index, 
            drawdown.values, 
            0, 
            color='red', 
            alpha=0.3,
            label=f'Max Drawdown: {drawdown.min():.1f}%'
        )
        ax.plot(drawdown.index, drawdown.values, color='red', linewidth=1)
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Drawdown (%)', fontsize=12)
        ax.legend(loc='lower left', fontsize=10)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.xticks(rotation=45)
        
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        return fig
    
    def plot_holdings_over_time(
        self, 
        positions_history: List[Dict],
        title: str = "Portfolio Holdings Over Time"
    ) -> plt.Figure:
        """Plot number of holdings over time."""
        fig, ax = plt.subplots(figsize=self.figsize)
        
        dates = [p['date'] for p in positions_history]
        num_holdings = [len(p['positions']) for p in positions_history]
        
        ax.plot(dates, num_holdings, linewidth=2)
        ax.fill_between(dates, num_holdings, alpha=0.3)
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Number of Holdings', fontsize=12)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.xticks(rotation=45)
        
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        return fig
    
    def plot_sector_allocation(
        self, 
        sector_weights: Dict[str, float],
        title: str = "Sector Allocation"
    ) -> plt.Figure:
        """Plot sector allocation pie chart."""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Sort sectors by weight
        sorted_sectors = sorted(sector_weights.items(), key=lambda x: x[1], reverse=True)
        sectors = [s[0] for s in sorted_sectors]
        weights = [s[1] for s in sorted_sectors]
        
        # Create pie chart
        colors = plt.cm.Set3(np.linspace(0, 1, len(sectors)))
        wedges, texts, autotexts = ax.pie(
            weights,
            labels=sectors,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors
        )
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        
        # Improve text
        for text in texts:
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_fontweight('bold')
        
        plt.tight_layout()
        return fig
    
    def plot_monthly_returns_heatmap(
        self, 
        portfolio_values: pd.DataFrame,
        title: str = "Monthly Returns Heatmap"
    ) -> plt.Figure:
        """Plot monthly returns heatmap."""
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Calculate monthly returns
        monthly_values = portfolio_values['value'].resample('M').last()
        monthly_returns = monthly_values.pct_change().dropna()
        
        # Reshape for heatmap
        returns_matrix = pd.DataFrame(index=range(1, 13), columns=[])
        
        for date, ret in monthly_returns.items():
            year = date.year
            month = date.month
            if year not in returns_matrix.columns:
                returns_matrix[year] = np.nan
            returns_matrix.loc[month, year] = ret * 100
        
        # Create heatmap
        sns.heatmap(
            returns_matrix,
            annot=True,
            fmt='.1f',
            cmap='RdYlGn',
            center=0,
            cbar_kws={'label': 'Return (%)'},
            ax=ax
        )
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('Month', fontsize=12)
        ax.set_yticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
        
        plt.tight_layout()
        return fig