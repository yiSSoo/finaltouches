"""
Chart Panel - Simple price chart with signal markers
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from datetime import datetime
import pandas as pd

# Set matplotlib to use dark theme
plt.style.use('dark_background')

class ChartPanel(QFrame):
    """Panel displaying price chart with signal markers"""
    
    def __init__(self, engine, config):
        super().__init__()
        self.engine = engine
        self.config = config
        
        self.setProperty("class", "panel")
        self.setup_ui()
        
        # Chart data tracking
        self.last_signal = None
        self.signal_markers = []
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("PRICE CHART")
        title.setProperty("class", "header")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Timeframe selector (future enhancement)
        timeframe_combo = QComboBox()
        timeframe_combo.addItems(["1m", "5m", "15m", "1h"])
        timeframe_combo.setCurrentText("1m")
        timeframe_combo.setMaximumWidth(60)
        header_layout.addWidget(timeframe_combo)
        
        layout.addLayout(header_layout)
        
        # Chart
        self.setup_chart()
        layout.addWidget(self.canvas)
        
    def setup_chart(self):
        """Setup matplotlib chart"""
        self.figure = Figure(figsize=(10, 6), facecolor='#1E1E1E')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: #1E1E1E;")
        
        # Create subplot
        self.ax = self.figure.add_subplot(111, facecolor='#1E1E1E')
        
        # Style the axes
        self.ax.tick_params(colors='#E0E0E0', which='both')
        self.ax.xaxis.label.set_color('#E0E0E0')
        self.ax.yaxis.label.set_color('#E0E0E0')
        self.ax.title.set_color('#E0E0E0')
        
        # Grid
        self.ax.grid(True, alpha=0.3, color='#404040')
        
        # Tight layout
        self.figure.tight_layout()
        
        # Initialize empty plot
        self.price_line, = self.ax.plot([], [], color='#2196F3', linewidth=1.5, label='NQ Price')
        self.ax.legend(loc='upper left', fancybox=True, framealpha=0.9)
        
    def update_data(self):
        """Update chart with latest data"""
        try:
            # Get current data from engine
            current_data = self.engine.get_current_data()
            
            # Get price history from engine dataframe
            if hasattr(self.engine, 'df') and not self.engine.df.empty:
                df = self.engine.df.copy()
                
                # Limit to last 100 bars for performance
                if len(df) > 100:
                    df = df.tail(100)
                
                if len(df) > 0:
                    self._plot_price_data(df, current_data)
            else:
                self._plot_no_data()
                
        except Exception as e:
            print(f"Error updating chart: {e}")
            self._plot_no_data()
    
    def _plot_price_data(self, df, current_data):
        """Plot price data with indicators"""
        self.ax.clear()
        
        # Plot price line
        timestamps = df.index
        prices = df['Close']
        
        self.ax.plot(timestamps, prices, color='#2196F3', linewidth=1.5, label='NQ Price')
        
        # Add EMA lines if available
        indicators_df = self.engine.indicator_engine.compute_indicators(df)
        if not indicators_df.empty and 'EMA9' in indicators_df.columns:
            if not indicators_df['EMA9'].isna().all():
                self.ax.plot(timestamps, indicators_df['EMA9'], color='#FF9800', 
                           linewidth=1, alpha=0.8, label='EMA 9')
            
            if not indicators_df['EMA21'].isna().all():
                self.ax.plot(timestamps, indicators_df['EMA21'], color='#4CAF50', 
                           linewidth=1, alpha=0.8, label='EMA 21')
        
        # Add VWAP if available
        if 'VWAP' in indicators_df.columns and not indicators_df['VWAP'].isna().all():
            self.ax.plot(timestamps, indicators_df['VWAP'], color='#9C27B0', 
                        linewidth=1, alpha=0.8, linestyle='--', label='VWAP')
        
        # Add signal markers (future enhancement)
        current_signal = current_data.get('bias', 'NEUTRAL')
        if current_signal != self.last_signal and len(timestamps) > 0:
            # Mark signal change
            marker_color = '#4CAF50' if current_signal == 'BULLISH' else '#F44336' if current_signal == 'BEARISH' else '#FFC107'
            self.ax.scatter([timestamps.iloc[-1]], [prices.iloc[-1]], 
                          c=marker_color, s=50, alpha=0.8, zorder=5)
            self.last_signal = current_signal
        
        # Formatting
        self.ax.set_title(f'NQ Futures - Last: {current_data.get("price", 0):.2f}', 
                         color='#E0E0E0', fontsize=10)
        
        # Format x-axis
        if len(timestamps) > 20:
            # Show fewer time labels for readability
            self.ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=max(1, len(timestamps)//10)))
        
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        
        # Rotate time labels
        self.figure.autofmt_xdate()
        
        # Style
        self.ax.tick_params(colors='#E0E0E0', which='both', labelsize=8)
        self.ax.grid(True, alpha=0.2, color='#404040')
        self.ax.set_facecolor('#1E1E1E')
        
        # Legend
        legend = self.ax.legend(loc='upper left', fancybox=True, framealpha=0.9, fontsize=8)
        legend.get_frame().set_facecolor('#2D2D2D')
        legend.get_frame().set_edgecolor('#404040')
        for text in legend.get_texts():
            text.set_color('#E0E0E0')
        
        # Refresh canvas
        self.canvas.draw()
    
    def _plot_no_data(self):
        """Show no data available message"""
        self.ax.clear()
        self.ax.text(0.5, 0.5, 'No Data Available\nWaiting for price feed...', 
                    horizontalalignment='center', verticalalignment='center',
                    transform=self.ax.transAxes, color='#B0B0B0', fontsize=12)
        self.ax.set_facecolor('#1E1E1E')
        self.canvas.draw()