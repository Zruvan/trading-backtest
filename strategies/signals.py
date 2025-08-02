"""Signal generation utilities."""
import logging
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class SignalGenerator:
    """Utilities for generating trading signals."""
    
    @staticmethod
    def buy_and_hold(symbols: List[str]) -> pd.Series:
        """
        Generate buy and hold signals (always buy).
        
        Args:
            symbols: List of stock symbols
        
        Returns:
            Series with buy signals (1) for all symbols
        """
        return pd.Series(1, index=symbols)
    
    @staticmethod
    def momentum_signals(
        price_data: Dict[str, pd.DataFrame],
        symbols: List[str],
        short_window: int = 20,
        long_window: int = 50
    ) -> pd.Series:
        """
        Generate momentum-based signals using moving averages.
        
        Args:
            price_data: Dictionary mapping symbols to price DataFrames
            symbols: List of stock symbols
            short_window: Short-term moving average window
            long_window: Long-term moving average window
        
        Returns:
            Series with signals (1=buy, 0=hold, -1=sell)
        """
        signals = {}
        
        for symbol in symbols:
            if symbol not in price_data:
                signals[symbol] = 0
                continue
            
            prices = price_data[symbol]
            if 'close' not in prices.columns or len(prices) < long_window:
                signals[symbol] = 0
                continue
            
            # Calculate moving averages
            short_ma = prices['close'].rolling(window=short_window).mean()
            long_ma = prices['close'].rolling(window=long_window).mean()
            
            # Generate signal based on crossover
            if len(short_ma) > 0 and len(long_ma) > 0:
                latest_short = short_ma.iloc[-1]
                latest_long = long_ma.iloc[-1]
                
                if pd.notna(latest_short) and pd.notna(latest_long):
                    if latest_short > latest_long:
                        signals[symbol] = 1  # Buy signal
                    else:
                        signals[symbol] = -1  # Sell signal
                else:
                    signals[symbol] = 0  # Hold
            else:
                signals[symbol] = 0
        
        return pd.Series(signals)
    
    @staticmethod
    def rsi_signals(
        price_data: Dict[str, pd.DataFrame],
        symbols: List[str],
        rsi_window: int = 14,
        oversold_threshold: float = 30,
        overbought_threshold: float = 70
    ) -> pd.Series:
        """
        Generate RSI-based signals.
        
        Args:
            price_data: Dictionary mapping symbols to price DataFrames
            symbols: List of stock symbols
            rsi_window: RSI calculation window
            oversold_threshold: RSI oversold threshold
            overbought_threshold: RSI overbought threshold
        
        Returns:
            Series with signals (1=buy, 0=hold, -1=sell)
        """
        signals = {}
        
        for symbol in symbols:
            if symbol not in price_data:
                signals[symbol] = 0
                continue
            
            prices = price_data[symbol]
            if 'close' not in prices.columns or len(prices) < rsi_window + 1:
                signals[symbol] = 0
                continue
            
            # Calculate RSI
            rsi = SignalGenerator._calculate_rsi(prices['close'], rsi_window)
            
            if len(rsi) > 0 and pd.notna(rsi.iloc[-1]):
                latest_rsi = rsi.iloc[-1]
                
                if latest_rsi < oversold_threshold:
                    signals[symbol] = 1  # Buy signal (oversold)
                elif latest_rsi > overbought_threshold:
                    signals[symbol] = -1  # Sell signal (overbought)
                else:
                    signals[symbol] = 0  # Hold
            else:
                signals[symbol] = 0
        
        return pd.Series(signals)
    
    @staticmethod
    def _calculate_rsi(prices: pd.Series, window: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI).
        
        Args:
            prices: Price series
            window: RSI calculation window
        
        Returns:
            RSI series
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()  # type: ignore
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()  # type: ignore
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def bollinger_band_signals(
        price_data: Dict[str, pd.DataFrame],
        symbols: List[str],
        window: int = 20,
        num_std: float = 2.0
    ) -> pd.Series:
        """
        Generate Bollinger Band-based signals.
        
        Args:
            price_data: Dictionary mapping symbols to price DataFrames
            symbols: List of stock symbols
            window: Moving average window
            num_std: Number of standard deviations for bands
        
        Returns:
            Series with signals (1=buy, 0=hold, -1=sell)
        """
        signals = {}
        
        for symbol in symbols:
            if symbol not in price_data:
                signals[symbol] = 0
                continue
            
            prices = price_data[symbol]
            if 'close' not in prices.columns or len(prices) < window:
                signals[symbol] = 0
                continue
            
            # Calculate Bollinger Bands
            close_prices = prices['close']
            moving_avg = close_prices.rolling(window=window).mean()
            std_dev = close_prices.rolling(window=window).std()
            
            lower_band = moving_avg - (std_dev * num_std)
            upper_band = moving_avg + (std_dev * num_std)
            
            if len(close_prices) > 0:
                latest_price = close_prices.iloc[-1]
                latest_lower = lower_band.iloc[-1]
                latest_upper = upper_band.iloc[-1]
                
                if (pd.notna(latest_lower) and pd.notna(latest_upper) and 
                    pd.notna(latest_price)):
                    
                    if latest_price < latest_lower:
                        signals[symbol] = 1  # Buy signal (price below lower band)
                    elif latest_price > latest_upper:
                        signals[symbol] = -1  # Sell signal (price above upper band)
                    else:
                        signals[symbol] = 0  # Hold
                else:
                    signals[symbol] = 0
            else:
                signals[symbol] = 0
        
        return pd.Series(signals)
    
    @staticmethod
    def volume_breakout_signals(
        price_data: Dict[str, pd.DataFrame],
        symbols: List[str],
        volume_window: int = 20,
        volume_multiplier: float = 2.0,
        price_change_threshold: float = 0.02
    ) -> pd.Series:
        """
        Generate volume breakout signals.
        
        Args:
            price_data: Dictionary mapping symbols to price DataFrames
            symbols: List of stock symbols
            volume_window: Window for average volume calculation
            volume_multiplier: Volume multiplier for breakout detection
            price_change_threshold: Minimum price change for signal
        
        Returns:
            Series with signals (1=buy, 0=hold, -1=sell)
        """
        signals = {}
        
        for symbol in symbols:
            if symbol not in price_data:
                signals[symbol] = 0
                continue
            
            prices = price_data[symbol]
            required_cols = ['close', 'volume']
            if not all(col in prices.columns for col in required_cols) or len(prices) < volume_window:
                signals[symbol] = 0
                continue
            
            # Calculate average volume
            avg_volume = prices['volume'].rolling(window=volume_window).mean()
            
            if len(prices) > 1 and len(avg_volume) > 0:
                latest_volume = prices['volume'].iloc[-1]
                latest_avg_volume = avg_volume.iloc[-1]
                
                # Calculate price change
                prev_close = prices['close'].iloc[-2]
                current_close = prices['close'].iloc[-1]
                price_change = (current_close - prev_close) / prev_close
                
                if (pd.notna(latest_avg_volume) and pd.notna(latest_volume) and
                    pd.notna(price_change)):
                    
                    # Check for volume breakout
                    volume_breakout = latest_volume > (latest_avg_volume * volume_multiplier)
                    significant_price_move = abs(price_change) > price_change_threshold
                    
                    if volume_breakout and significant_price_move:
                        if price_change > 0:
                            signals[symbol] = 1  # Buy on upward breakout
                        else:
                            signals[symbol] = -1  # Sell on downward breakout
                    else:
                        signals[symbol] = 0  # Hold
                else:
                    signals[symbol] = 0
            else:
                signals[symbol] = 0
        
        return pd.Series(signals)
    
    @staticmethod
    def combine_signals(
        signal_series: List[pd.Series],
        method: str = 'majority',
        weights: Optional[List[float]] = None
    ) -> pd.Series:
        """
        Combine multiple signal series.
        
        Args:
            signal_series: List of signal Series to combine
            method: Combination method ('majority', 'unanimous', 'weighted')
            weights: Weights for weighted combination (if method='weighted')
        
        Returns:
            Combined signal series
        """
        if not signal_series:
            return pd.Series()
        
        if len(signal_series) == 1:
            return signal_series[0]
        
        # Align all series
        combined_index = signal_series[0].index
        for series in signal_series[1:]:
            combined_index = combined_index.union(series.index)
        
        aligned_signals = []
        for series in signal_series:
            aligned = series.reindex(combined_index, fill_value=0)
            aligned_signals.append(aligned)
        
        if method == 'majority':
            # Take majority vote
            signal_matrix = pd.DataFrame(aligned_signals).T
            combined = signal_matrix.apply(lambda row: row.mode().iloc[0] if len(row.mode()) > 0 else 0, axis=1)
        
        elif method == 'unanimous':
            # All signals must agree
            signal_matrix = pd.DataFrame(aligned_signals).T
            combined = signal_matrix.apply(
                lambda row: row.iloc[0] if (row == row.iloc[0]).all() else 0, 
                axis=1
            )
        
        elif method == 'weighted':
            if weights is None or len(weights) != len(signal_series):
                raise ValueError("Weights must be provided and match number of signal series")
            
            # Weighted average of signals
            signal_matrix = pd.DataFrame(aligned_signals).T
            combined = signal_matrix.apply(
                lambda row: np.sign(np.average(row, weights=weights)), 
                axis=1
            ).astype(int)
        
        else:
            raise ValueError("Method must be 'majority', 'unanimous', or 'weighted'")
        
        return combined
