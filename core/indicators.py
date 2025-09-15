"""
Technical indicators calculation engine
"""

import numpy as np
import pandas as pd
from typing import Tuple

class IndicatorEngine:
    """Calculate technical indicators for trading signals"""
    
    def __init__(self, config):
        self.config = config
    
    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute all technical indicators"""
        if df.empty or len(df) < 50:  # Need minimum bars for indicators
            return df.copy()
        
        result = df.copy()
        
        # Exponential Moving Averages
        result["EMA9"] = self._ema(result["Close"], 9)
        result["EMA21"] = self._ema(result["Close"], 21)
        result["EMA50"] = self._ema(result["Close"], 50)
        
        # MACD
        macd_line, macd_signal, macd_hist = self._macd(result["Close"])
        result["MACD"] = macd_line
        result["MACDsig"] = macd_signal
        result["MACDhist"] = macd_hist
        
        # RSI
        result["RSI14"] = self._rsi(result["Close"], 14)
        
        # Stochastic
        result["StochK"] = self._stochastic_k(result["High"], result["Low"], result["Close"])
        result["StochD"] = result["StochK"].rolling(3).mean()
        
        # Bollinger Bands
        bb_mid, bb_upper, bb_lower = self._bollinger_bands(result["Close"])
        result["BBmid"] = bb_mid
        result["BBup"] = bb_upper
        result["BBlo"] = bb_lower
        
        # VWAP (session-based)
        result["VWAP"] = self._session_vwap(result)
        
        return result
    
    def _ema(self, series: pd.Series, span: int) -> pd.Series:
        """Exponential Moving Average"""
        return series.ewm(span=span, adjust=False).mean()
    
    def _rsi(self, series: pd.Series, length: int = 14) -> pd.Series:
        """Relative Strength Index"""
        delta = series.diff()
        up = delta.clip(lower=0).rolling(length).mean()
        down = (-delta.clip(upper=0)).rolling(length).mean()
        
        rs = up / down.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _stochastic_k(self, high: pd.Series, low: pd.Series, close: pd.Series, k: int = 14) -> pd.Series:
        """Stochastic %K"""
        lowest_low = low.rolling(k).min()
        highest_high = high.rolling(k).max()
        
        k_percent = 100 * (close - lowest_low) / (highest_high - lowest_low).replace(0, np.nan)
        return k_percent
    
    def _macd(self, series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """MACD indicator"""
        ema_fast = self._ema(series, fast)
        ema_slow = self._ema(series, slow)
        
        macd_line = ema_fast - ema_slow
        macd_signal = self._ema(macd_line, signal)
        macd_histogram = macd_line - macd_signal
        
        return macd_line, macd_signal, macd_histogram
    
    def _bollinger_bands(self, series: pd.Series, length: int = 20, mult: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Bollinger Bands"""
        middle = series.rolling(length).mean()
        std = series.rolling(length).std(ddof=0)
        
        upper = middle + (mult * std)
        lower = middle - (mult * std)
        
        return middle, upper, lower
    
    def _session_vwap(self, df: pd.DataFrame) -> pd.Series:
        """Volume Weighted Average Price (session-based)"""
        if df.empty or "Volume" not in df.columns:
            return pd.Series(index=df.index, dtype=float)
        
        # Calculate typical price
        typical_price = (df["High"] + df["Low"] + df["Close"]) / 3.0
        
        # Handle zero/NaN volumes
        volume = df["Volume"].fillna(0)
        volume = volume.replace(0, 1)  # Avoid division by zero
        
        # Calculate VWAP
        vwap = (typical_price * volume).cumsum() / volume.cumsum()
        
        return vwap