"""
Trading signal generation and confluence analysis
"""

import numpy as np
import pandas as pd
from typing import Tuple, List, Dict
from datetime import datetime

# Timezone
try:
    from zoneinfo import ZoneInfo
    ET = ZoneInfo("America/New_York")
except ImportError:
    from datetime import timezone, timedelta
    ET = timezone(timedelta(hours=-5))

def now_et():
    return datetime.now(ET)

class SignalEngine:
    """Generate trading signals based on technical analysis"""
    
    def __init__(self, config):
        self.config = config
    
    def generate_signal(self, df: pd.DataFrame) -> Tuple[str, int, List[str]]:
        """Generate primary trading signal"""
        if df.empty or len(df) < 10:
            return "NEUTRAL", 50, ["Insufficient data"]
        
        latest_row = df.iloc[-1]
        return self._analyze_bias(latest_row)
    
    def confluence_analysis(self, df: pd.DataFrame, or_high: float = None, 
                          or_low: float = None, or_ready: bool = False) -> Tuple[int, List[str]]:
        """Comprehensive confluence analysis with SHORT bias"""
        if df.empty or len(df) < 30:
            return 50, ["Warming up - need more data"]
        
        score = 50  # Start neutral
        reasons = []
        
        # Get multi-timeframe data
        frames = self._create_timeframes(df)
        
        # Higher timeframe bias
        for tf, weight in [("4h", 15), ("60m", 10), ("15m", 8)]:
            if tf in frames and not frames[tf].empty:
                tf_bias, tf_score, _ = self._analyze_bias(frames[tf].iloc[-1])
                if tf_bias == "BEARISH":
                    score += weight
                    reasons.append(f"{tf} bearish trend")
                elif tf_bias == "BULLISH":
                    score -= weight * 0.7  # Slightly less penalty for bull
                    reasons.append(f"{tf} bullish trend")
        
        # Current 1m analysis
        latest = df.iloc[-1]
        
        # EMA stack analysis
        if latest["Close"] < latest["EMA9"] < latest["EMA21"] < latest["EMA50"]:
            score += 8
            reasons.append("Complete bear EMA stack")
        elif latest["EMA9"] < latest["EMA21"] < latest["EMA50"]:
            score += 4
            reasons.append("Partial bear EMA stack")
        
        # MACD momentum
        if latest["MACD"] < latest["MACDsig"] and latest["MACDhist"] < 0:
            score += 5
            reasons.append("MACD bearish momentum")
        
        # RSI conditions
        if latest["RSI14"] >= 70:
            score += 6
            reasons.append("RSI overbought (>70)")
        elif latest["RSI14"] >= 60:
            score += 3
            reasons.append("RSI elevated (>60)")
        elif latest["RSI14"] <= 30:
            score -= 4
            reasons.append("RSI oversold (<30)")
        
        # Bollinger Bands
        if latest["Close"] > latest["BBup"]:
            score += 6
            reasons.append("Price above upper Bollinger Band")
        elif latest["Close"] < latest["BBlo"]:
            score -= 3
            reasons.append("Price below lower Bollinger Band")
        
        # VWAP analysis
        if not np.isnan(latest["VWAP"]):
            if latest["Close"] < latest["VWAP"]:
                score += 4
                reasons.append("Below session VWAP")
            else:
                score -= 2
                reasons.append("Above session VWAP")
        
        # Opening Range analysis
        if or_ready and or_low is not None and latest["Close"] < or_low:
            score += 8
            reasons.append("Opening Range low break")
        elif or_ready and or_high is not None and latest["Close"] > or_high:
            score -= 5
            reasons.append("Opening Range high break")
        
        # Stochastic
        if latest["StochK"] < latest["StochD"] and latest["StochK"] > 80:
            score += 4
            reasons.append("Stochastic bear cross from overbought")
        
        # Volume consideration (if available)
        if len(df) >= 20:
            avg_volume = df["Volume"].tail(20).mean()
            current_volume = latest["Volume"]
            if current_volume > avg_volume * 1.5:
                if score > 50:  # If already bearish
                    score += 3
                    reasons.append("High volume confirms bear signal")
        
        # Ensure score stays in bounds
        final_score = max(0, min(100, int(score)))
        
        return final_score, reasons[:8]  # Limit reasons for display
    
    def _analyze_bias(self, row: pd.Series) -> Tuple[str, int, List[str]]:
        """Analyze single row for bias"""
        score = 50
        reasons = []
        
        # EMA relationships
        if row["Close"] < row["EMA9"] < row["EMA21"] < row["EMA50"]:
            score += 10
            reasons.append("Complete bear EMA stack")
        elif row["Close"] > row["EMA9"] > row["EMA21"] > row["EMA50"]:
            score -= 10
            reasons.append("Complete bull EMA stack")
        elif row["Close"] < row["EMA9"]:
            score += 4
            reasons.append("Below fast EMA")
        elif row["Close"] > row["EMA9"]:
            score -= 4
            reasons.append("Above fast EMA")
        
        # VWAP
        if not np.isnan(row.get("VWAP", np.nan)):
            if row["Close"] < row["VWAP"]:
                score += 4
                reasons.append("Below VWAP")
            else:
                score -= 2
                reasons.append("Above VWAP")
        
        # MACD
        if row["MACD"] < row["MACDsig"]:
            score += 4
            reasons.append("MACD bearish")
        else:
            score -= 2
            reasons.append("MACD bullish")
        
        # RSI extremes
        if row["RSI14"] >= 70:
            score += 6
            reasons.append("RSI overbought")
        elif row["RSI14"] <= 30:
            score -= 4
            reasons.append("RSI oversold")
        
        # Bollinger Bands
        if row["Close"] > row.get("BBup", np.inf):
            score += 6
            reasons.append("Outside upper band")
        elif row["Close"] < row.get("BBlo", -np.inf):
            score -= 3
            reasons.append("Outside lower band")
        
        # Determine bias
        final_score = max(0, min(100, int(score)))
        
        if final_score >= 65:
            bias = "BEARISH"
        elif final_score <= 35:
            bias = "BULLISH"
        else:
            bias = "NEUTRAL"
        
        return bias, final_score, reasons
    
    def _create_timeframes(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Create higher timeframe data"""
        if df.empty:
            return {}
        
        frames = {"1m": df}
        
        # Aggregation rules
        agg_rules = {
            "Open": "first",
            "High": "max",
            "Low": "min",
            "Close": "last",
            "Volume": "sum"
        }
        
        # Create timeframes
        timeframe_configs = {
            "5m": "5min",
            "15m": "15min", 
            "60m": "60min",
            "4h": "240min"
        }
        
        for tf_name, tf_rule in timeframe_configs.items():
            try:
                tf_df = df.resample(tf_rule).agg(agg_rules).dropna()
                if tf_df.empty:
                    continue
                
                # Add basic indicators to higher timeframes
                tf_df["EMA9"] = tf_df["Close"].ewm(span=9, adjust=False).mean()
                tf_df["EMA21"] = tf_df["Close"].ewm(span=21, adjust=False).mean()
                tf_df["EMA50"] = tf_df["Close"].ewm(span=50, adjust=False).mean()
                
                # MACD
                ema12 = tf_df["Close"].ewm(span=12, adjust=False).mean()
                ema26 = tf_df["Close"].ewm(span=26, adjust=False).mean()
                tf_df["MACD"] = ema12 - ema26
                tf_df["MACDsig"] = tf_df["MACD"].ewm(span=9, adjust=False).mean()
                
                # RSI
                delta = tf_df["Close"].diff()
                up = delta.clip(lower=0).rolling(14).mean()
                down = (-delta.clip(upper=0)).rolling(14).mean()
                rs = up / down.replace(0, np.nan)
                tf_df["RSI14"] = 100 - (100 / (1 + rs))
                
                # Bollinger Bands
                bb_mid = tf_df["Close"].rolling(20).mean()
                bb_std = tf_df["Close"].rolling(20).std(ddof=0)
                tf_df["BBmid"] = bb_mid
                tf_df["BBup"] = bb_mid + (2.0 * bb_std)
                tf_df["BBlo"] = bb_mid - (2.0 * bb_std)
                
                frames[tf_name] = tf_df
                
            except Exception as e:
                print(f"Error creating {tf_name} timeframe: {e}")
                continue
        
        return frames