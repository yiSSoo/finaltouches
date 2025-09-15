"""
Core trading engine for NQ Master v3
Handles data collection, OCR, indicators, and signal generation
"""

import time
import threading
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple, Optional
from PyQt5.QtCore import QObject, pyqtSignal

from .data_feeds import YahooFeed, OCRFeed
from .indicators import IndicatorEngine
from .signals import SignalEngine
from .news import NewsFeed

# Timezone handling
try:
    from zoneinfo import ZoneInfo
    ET = ZoneInfo("America/New_York")
except ImportError:
    ET = timezone(timedelta(hours=-5))

def now_et():
    return datetime.now(ET)

class TradingEngine(QObject):
    """Main trading engine coordinating all components"""
    
    # Signals for UI updates
    price_updated = pyqtSignal(float, str)  # price, source
    signal_updated = pyqtSignal(str, int, list)  # bias, confidence, reasons
    confluence_updated = pyqtSignal(int, list)  # score, reasons
    news_updated = pyqtSignal(list)  # news items
    error_occurred = pyqtSignal(str)  # error message
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self._running = False
        self._stop_event = threading.Event()
        
        # Core data
        self.df = pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])
        self.current_price = 0.0
        self.current_source = "YAHOO"
        
        # Initialize components
        self.yahoo_feed = YahooFeed(config)
        self.ocr_feed = OCRFeed(config)
        self.indicator_engine = IndicatorEngine(config)
        self.signal_engine = SignalEngine(config)
        self.news_feed = NewsFeed(config)
        
        # Opening Range tracking
        self.or_high = None
        self.or_low = None
        self.or_ready = False
        
        # Signal tracking for chimes
        self.last_bias = None
        
    def start(self):
        """Start the trading engine"""
        if self._running:
            return
            
        self._running = True
        self._stop_event.clear()
        
        # Start data feeds
        self.yahoo_feed.start()
        self.ocr_feed.start()
        self.news_feed.start()
        
        # Start main processing thread
        self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
        self.processing_thread.start()
        
    def stop(self):
        """Stop the trading engine"""
        if not self._running:
            return
            
        self._running = False
        self._stop_event.set()
        
        # Stop data feeds
        self.yahoo_feed.stop()
        self.ocr_feed.stop()
        self.news_feed.stop()
        
    def get_current_data(self) -> Dict:
        """Get current trading data snapshot"""
        if self.df.empty:
            return {
                "price": 0.0,
                "source": "NONE",
                "bias": "NEUTRAL",
                "confidence": 0,
                "indicators": {},
                "or_high": None,
                "or_low": None
            }
        
        # Get latest indicators
        indicators_df = self.indicator_engine.compute_indicators(self.df)
        if indicators_df.empty:
            return {"price": self.current_price, "source": self.current_source}
        
        latest_row = indicators_df.iloc[-1]
        
        # Get current signal
        bias, confidence, reasons = self.signal_engine.generate_signal(indicators_df)
        
        return {
            "price": self.current_price,
            "source": self.current_source,
            "bias": bias,
            "confidence": confidence,
            "reasons": reasons,
            "indicators": {
                "ema9": latest_row.get("EMA9", 0),
                "ema21": latest_row.get("EMA21", 0),
                "ema50": latest_row.get("EMA50", 0),
                "vwap": latest_row.get("VWAP", 0),
                "rsi": latest_row.get("RSI14", 0),
                "macd": latest_row.get("MACD", 0),
                "macd_signal": latest_row.get("MACDsig", 0),
            },
            "or_high": self.or_high,
            "or_low": self.or_low,
            "or_ready": self.or_ready
        }
    
    def get_confluence_analysis(self) -> Tuple[int, List[str]]:
        """Get confluence analysis"""
        if self.df.empty:
            return 50, ["No data available"]
        
        indicators_df = self.indicator_engine.compute_indicators(self.df)
        return self.signal_engine.confluence_analysis(indicators_df, self.or_high, self.or_low, self.or_ready)
    
    def get_news_data(self) -> List[Dict]:
        """Get current news data"""
        return self.news_feed.get_news_items()
    
    def auto_locate_dom(self):
        """Trigger DOM auto-location"""
        self.ocr_feed.auto_locate()
    
    def set_dom_region(self, bbox: Dict[str, int]):
        """Set DOM region manually"""
        self.ocr_feed.set_bbox(bbox)
        self.config.bbox = bbox
        self.config.save()
    
    def _processing_loop(self):
        """Main processing loop"""
        while self._running and not self._stop_event.is_set():
            try:
                self._update_data()
                self._compute_signals()
                self._update_opening_range()
                
            except Exception as e:
                self.error_occurred.emit(f"Processing error: {e}")
            
            # Wait for next cycle
            self._stop_event.wait(self.config.ocr_poll_sec)
    
    def _update_data(self):
        """Update price data from feeds"""
        # Get Yahoo data
        yahoo_data = self.yahoo_feed.get_latest_data()
        if yahoo_data is not None and not yahoo_data.empty:
            # Update main dataframe
            for timestamp, row in yahoo_data.iterrows():
                self.df.loc[timestamp] = row
            self.df.sort_index(inplace=True)
        
        # Get OCR price
        ocr_price = self.ocr_feed.get_latest_price()
        
        # Determine current price and source
        if ocr_price is not None:
            self.current_price = ocr_price
            self.current_source = "OCR"
            
            # Splice OCR price into current bar
            self._splice_ocr_price(ocr_price)
        else:
            # Use Yahoo price
            if not self.df.empty:
                self.current_price = float(self.df.iloc[-1]["Close"])
                self.current_source = "YAHOO"
        
        # Emit price update
        self.price_updated.emit(self.current_price, self.current_source)
    
    def _splice_ocr_price(self, ocr_price: float):
        """Splice OCR price into current minute bar"""
        if self.df.empty:
            return
        
        # Get current minute timestamp
        current_time = now_et().replace(second=0, microsecond=0)
        
        if current_time in self.df.index:
            # Update existing bar
            bar = self.df.loc[current_time].copy()
            bar["Close"] = ocr_price
            bar["High"] = max(bar["High"], ocr_price)
            bar["Low"] = min(bar["Low"], ocr_price)
            self.df.loc[current_time] = bar
        else:
            # Create new bar
            prev_close = float(self.df.iloc[-1]["Close"]) if not self.df.empty else ocr_price
            new_bar = {
                "Open": prev_close,
                "High": max(prev_close, ocr_price),
                "Low": min(prev_close, ocr_price),
                "Close": ocr_price,
                "Volume": 0
            }
            self.df.loc[current_time] = new_bar
            self.df.sort_index(inplace=True)
    
    def _compute_signals(self):
        """Compute and emit trading signals"""
        if self.df.empty:
            return
        
        # Compute indicators
        indicators_df = self.indicator_engine.compute_indicators(self.df)
        if indicators_df.empty:
            return
        
        # Generate primary signal
        bias, confidence, reasons = self.signal_engine.generate_signal(indicators_df)
        
        # Check for bias change and emit chime if needed
        if self.last_bias != bias:
            self.last_bias = bias
            # Could emit a chime signal here
        
        # Emit signal update
        self.signal_updated.emit(bias, confidence, reasons)
        
        # Generate confluence analysis
        conf_score, conf_reasons = self.signal_engine.confluence_analysis(
            indicators_df, self.or_high, self.or_low, self.or_ready
        )
        
        # Emit confluence update
        self.confluence_updated.emit(conf_score, conf_reasons)
    
    def _update_opening_range(self):
        """Update opening range calculations"""
        if self.df.empty:
            return
        
        # Define opening range period (9:30 AM - 9:30 AM + or_minutes)
        market_open = now_et().replace(hour=9, minute=30, second=0, microsecond=0)
        or_end = market_open + timedelta(minutes=self.config.or_minutes)
        
        # Get opening range data
        or_data = self.df.loc[(self.df.index >= market_open) & (self.df.index <= or_end)]
        
        if not or_data.empty:
            self.or_high = float(or_data["High"].max())
            self.or_low = float(or_data["Low"].min())
            self.or_ready = now_et() >= or_end