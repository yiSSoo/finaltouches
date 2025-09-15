"""
Price and Signal Panel - Main trading information display
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class PriceSignalPanel(QFrame):
    """Panel displaying current price and primary trading signal"""
    
    def __init__(self, engine, config):
        super().__init__()
        self.engine = engine
        self.config = config
        
        self.setProperty("class", "panel")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("LIVE PRICE & SIGNAL")
        title_label.setProperty("class", "header")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Source indicator
        self.source_label = QLabel("YAHOO")
        self.source_label.setStyleSheet("color: #FFC107; font-weight: bold; font-size: 9pt;")
        header_layout.addWidget(self.source_label)
        
        layout.addLayout(header_layout)
        
        # Price section
        price_frame = QFrame()
        price_layout = QVBoxLayout(price_frame)
        price_layout.setContentsMargins(0, 8, 0, 8)
        
        # Main price display
        price_container = QHBoxLayout()
        
        self.price_label = QLabel("0.00")
        self.price_label.setProperty("class", "price-large")
        self.price_label.setAlignment(Qt.AlignCenter)
        price_container.addWidget(self.price_label)
        
        price_layout.addLayout(price_container)
        
        # Price change (placeholder for future implementation)
        self.change_label = QLabel("+0.00 (+0.00%)")
        self.change_label.setAlignment(Qt.AlignCenter)
        self.change_label.setStyleSheet("color: #4CAF50; font-size: 11pt;")
        price_layout.addWidget(self.change_label)
        
        layout.addWidget(price_frame)
        
        # Signal section
        signal_frame = QFrame()
        signal_layout = QVBoxLayout(signal_frame)
        signal_layout.setContentsMargins(0, 8, 0, 8)
        
        # Signal header
        signal_header = QLabel("LIVE SIGNAL")
        signal_header.setProperty("class", "subheader")
        signal_header.setAlignment(Qt.AlignCenter)
        signal_layout.addWidget(signal_header)
        
        # Signal display
        signal_container = QHBoxLayout()
        signal_container.setAlignment(Qt.AlignCenter)
        
        self.signal_label = QLabel("NEUTRAL")
        self.signal_label.setProperty("class", "signal-neutral")
        self.signal_label.setAlignment(Qt.AlignCenter)
        self.signal_label.setMinimumWidth(120)
        signal_container.addWidget(self.signal_label)
        
        signal_layout.addLayout(signal_container)
        
        # Confidence display
        confidence_layout = QHBoxLayout()
        confidence_layout.setAlignment(Qt.AlignCenter)
        
        confidence_layout.addWidget(QLabel("Confidence:"))
        
        self.confidence_label = QLabel("50%")
        self.confidence_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        confidence_layout.addWidget(self.confidence_label)
        
        signal_layout.addLayout(confidence_layout)
        
        layout.addWidget(signal_frame)
        
        # Indicators section
        indicators_frame = QFrame()
        indicators_layout = QVBoxLayout(indicators_frame)
        indicators_layout.setContentsMargins(0, 8, 0, 0)
        
        # Indicators header
        indicators_header = QLabel("KEY INDICATORS")
        indicators_header.setProperty("class", "subheader")
        indicators_layout.addWidget(indicators_header)
        
        # Indicators grid
        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(6)
        
        # EMA indicators
        grid.addWidget(QLabel("EMA 9:"), 0, 0)
        self.ema9_label = QLabel("0.00")
        grid.addWidget(self.ema9_label, 0, 1)
        
        grid.addWidget(QLabel("EMA 21:"), 0, 2)
        self.ema21_label = QLabel("0.00")
        grid.addWidget(self.ema21_label, 0, 3)
        
        grid.addWidget(QLabel("EMA 50:"), 1, 0)
        self.ema50_label = QLabel("0.00")
        grid.addWidget(self.ema50_label, 1, 1)
        
        grid.addWidget(QLabel("VWAP:"), 1, 2)
        self.vwap_label = QLabel("0.00")
        grid.addWidget(self.vwap_label, 1, 3)
        
        # RSI and MACD
        grid.addWidget(QLabel("RSI:"), 2, 0)
        self.rsi_label = QLabel("50.0")
        grid.addWidget(self.rsi_label, 2, 1)
        
        grid.addWidget(QLabel("MACD:"), 2, 2)
        self.macd_label = QLabel("0.00")
        grid.addWidget(self.macd_label, 2, 3)
        
        indicators_layout.addLayout(grid)
        layout.addWidget(indicators_frame)
        
        # Opening Range section
        or_frame = QFrame()
        or_layout = QVBoxLayout(or_frame)
        or_layout.setContentsMargins(0, 8, 0, 0)
        
        or_header = QLabel("OPENING RANGE")
        or_header.setProperty("class", "subheader")
        or_layout.addWidget(or_header)
        
        or_grid = QGridLayout()
        or_grid.setHorizontalSpacing(16)
        
        or_grid.addWidget(QLabel("High:"), 0, 0)
        self.or_high_label = QLabel("--")
        or_grid.addWidget(self.or_high_label, 0, 1)
        
        or_grid.addWidget(QLabel("Low:"), 0, 2)
        self.or_low_label = QLabel("--")
        or_grid.addWidget(self.or_low_label, 0, 3)
        
        or_layout.addLayout(or_grid)
        layout.addWidget(or_frame)
        
        layout.addStretch()
    
    def update_data(self):
        """Update panel with latest data"""
        try:
            data = self.engine.get_current_data()
            
            # Update price
            price = data.get("price", 0.0)
            self.price_label.setText(f"{price:.2f}")
            
            # Update source indicator
            source = data.get("source", "NONE")
            self.source_label.setText(f"[{source}]")
            
            if source == "OCR":
                self.source_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 9pt;")
            elif source == "YAHOO":
                self.source_label.setStyleSheet("color: #FFC107; font-weight: bold; font-size: 9pt;")
            else:
                self.source_label.setStyleSheet("color: #F44336; font-weight: bold; font-size: 9pt;")
            
            # Update signal
            bias = data.get("bias", "NEUTRAL")
            confidence = data.get("confidence", 50)
            
            self.signal_label.setText(bias)
            self.confidence_label.setText(f"{confidence}%")
            
            # Update signal styling
            if bias == "BULLISH":
                self.signal_label.setProperty("class", "signal-bullish")
                self.confidence_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 11pt;")
            elif bias == "BEARISH":
                self.signal_label.setProperty("class", "signal-bearish")
                self.confidence_label.setStyleSheet("color: #F44336; font-weight: bold; font-size: 11pt;")
            else:
                self.signal_label.setProperty("class", "signal-neutral")
                self.confidence_label.setStyleSheet("color: #E0E0E0; font-weight: bold; font-size: 11pt;")
            
            # Force style update
            self.signal_label.style().unpolish(self.signal_label)
            self.signal_label.style().polish(self.signal_label)
            
            # Update indicators
            indicators = data.get("indicators", {})
            
            self.ema9_label.setText(f"{indicators.get('ema9', 0):.2f}")
            self.ema21_label.setText(f"{indicators.get('ema21', 0):.2f}")
            self.ema50_label.setText(f"{indicators.get('ema50', 0):.2f}")
            self.vwap_label.setText(f"{indicators.get('vwap', 0):.2f}")
            self.rsi_label.setText(f"{indicators.get('rsi', 0):.1f}")
            self.macd_label.setText(f"{indicators.get('macd', 0):.2f}")
            
            # Color code RSI
            rsi_val = indicators.get('rsi', 50)
            if rsi_val >= 70:
                self.rsi_label.setStyleSheet("color: #F44336; font-weight: bold;")  # Overbought
            elif rsi_val <= 30:
                self.rsi_label.setStyleSheet("color: #4CAF50; font-weight: bold;")  # Oversold
            else:
                self.rsi_label.setStyleSheet("color: #E0E0E0;")
            
            # Update Opening Range
            or_high = data.get("or_high")
            or_low = data.get("or_low")
            
            if or_high is not None:
                self.or_high_label.setText(f"{or_high:.2f}")
            else:
                self.or_high_label.setText("--")
            
            if or_low is not None:
                self.or_low_label.setText(f"{or_low:.2f}")
            else:
                self.or_low_label.setText("--")
                
        except Exception as e:
            print(f"Error updating price/signal panel: {e}")