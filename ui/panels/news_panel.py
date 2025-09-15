"""
News Panel - Market news feed and sentiment analysis
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime, timedelta

class NewsPanel(QFrame):
    """Panel displaying news feed and market sentiment"""
    
    def __init__(self, engine, config):
        super().__init__()
        self.engine = engine
        self.config = config
        
        self.setProperty("class", "panel")
        self.ticker_position = 0
        self.ticker_text = "Loading news feed..."
        
        self.setup_ui()
        
        # Ticker animation timer
        self.ticker_timer = QTimer()
        self.ticker_timer.timeout.connect(self.update_ticker)
        self.ticker_timer.start(100)  # Update ticker every 100ms
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Header
        header = QLabel("MARKET NEWS")
        header.setProperty("class", "header")
        layout.addWidget(header)
        
        # News ticker
        ticker_frame = QFrame()
        ticker_frame.setStyleSheet("""
            QFrame {
                background-color: #1565C0;
                border-radius: 4px;
                padding: 6px;
            }
        """)
        ticker_frame.setFixedHeight(30)
        
        ticker_layout = QHBoxLayout(ticker_frame)
        ticker_layout.setContentsMargins(8, 0, 8, 0)
        
        self.ticker_label = QLabel(self.ticker_text)
        self.ticker_label.setStyleSheet("color: #FFFFFF; font-size: 9pt; font-weight: 500;")
        ticker_layout.addWidget(self.ticker_label)
        
        layout.addWidget(ticker_frame)
        
        # Market sentiment
        sentiment_frame = QFrame()
        sentiment_layout = QHBoxLayout(sentiment_frame)
        sentiment_layout.setContentsMargins(0, 4, 0, 4)
        
        sentiment_layout.addWidget(QLabel("Market Sentiment:"))
        
        self.sentiment_label = QLabel("NEUTRAL")
        self.sentiment_label.setStyleSheet("font-weight: bold; padding: 2px 8px; background-color: #455A64; color: white; border-radius: 3px;")
        sentiment_layout.addWidget(self.sentiment_label)
        
        sentiment_layout.addStretch()
        
        layout.addWidget(sentiment_frame)
        
        # News table
        self.news_table = QTableWidget()
        self.news_table.setColumnCount(3)
        self.news_table.setHorizontalHeaderLabels(["Time", "Impact", "Event"])
        
        # Configure table
        header_view = self.news_table.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header_view.setStretchLastSection(True)
        
        self.news_table.setAlternatingRowColors(True)
        self.news_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.news_table.verticalHeader().setVisible(False)
        self.news_table.setWordWrap(True)
        
        # Set row height
        self.news_table.verticalHeader().setDefaultSectionSize(24)
        
        layout.addWidget(self.news_table)
    
    def update_data(self):
        """Update panel with latest news data"""
        try:
            news_items = self.engine.get_news_data()
            
            # Update ticker text
            if news_items:
                ticker_items = []
                for item in news_items[:5]:  # Use top 5 for ticker
                    impact_tag = self._get_impact_tag(item.get("impact", ""))
                    ticker_items.append(f"[{impact_tag}] {item.get('title', '')}")
                
                self.ticker_text = " • ".join(ticker_items)
                if len(self.ticker_text) > 500:  # Limit ticker length
                    self.ticker_text = self.ticker_text[:500] + "..."
            else:
                self.ticker_text = "Loading news feed..."
            
            # Update market sentiment
            if hasattr(self.engine.news_feed, 'get_market_sentiment'):
                sentiment = self.engine.news_feed.get_market_sentiment()
                self.sentiment_label.setText(sentiment)
                
                if sentiment == "BEARISH":
                    self.sentiment_label.setStyleSheet("font-weight: bold; padding: 2px 8px; background-color: #F44336; color: white; border-radius: 3px;")
                elif sentiment == "BULLISH":
                    self.sentiment_label.setStyleSheet("font-weight: bold; padding: 2px 8px; background-color: #4CAF50; color: white; border-radius: 3px;")
                else:
                    self.sentiment_label.setStyleSheet("font-weight: bold; padding: 2px 8px; background-color: #455A64; color: white; border-radius: 3px;")
            
            # Update news table
            self._update_news_table(news_items)
            
        except Exception as e:
            print(f"Error updating news panel: {e}")
    
    def _update_news_table(self, news_items):
        """Update the news table with latest items"""
        try:
            # Limit to recent items
            display_items = news_items[:20] if news_items else []
            
            self.news_table.setRowCount(len(display_items))
            
            for i, item in enumerate(display_items):
                # Time
                item_time = item.get("time", datetime.now())
                if isinstance(item_time, datetime):
                    time_str = item_time.strftime("%H:%M")
                    
                    # Show date if not today
                    if item_time.date() != datetime.now().date():
                        time_str = item_time.strftime("%m/%d")
                else:
                    time_str = "--:--"
                
                time_item = QTableWidgetItem(time_str)
                time_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                time_item.setTextAlignment(Qt.AlignCenter)
                self.news_table.setItem(i, 0, time_item)
                
                # Impact
                impact = item.get("impact", "")
                impact_item = QTableWidgetItem(self._get_impact_tag(impact))
                impact_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                impact_item.setTextAlignment(Qt.AlignCenter)
                
                # Color code impact
                if "High" in impact:
                    impact_item.setForeground(QColor("#F44336"))
                    impact_item.setBackground(QColor("#FFEBEE"))
                elif "Medium" in impact:
                    impact_item.setForeground(QColor("#FF9800"))
                    impact_item.setBackground(QColor("#FFF3E0"))
                else:
                    impact_item.setForeground(QColor("#4CAF50"))
                    impact_item.setBackground(QColor("#E8F5E8"))
                
                self.news_table.setItem(i, 1, impact_item)
                
                # Event title
                title = item.get("title", "")
                if len(title) > 60:
                    title = title[:60] + "..."
                
                title_item = QTableWidgetItem(title)
                title_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                title_item.setToolTip(item.get("title", ""))  # Full title in tooltip
                self.news_table.setItem(i, 2, title_item)
                
        except Exception as e:
            print(f"Error updating news table: {e}")
    
    def _get_impact_tag(self, impact):
        """Get short impact tag"""
        if "High" in impact:
            return "HIGH"
        elif "Medium" in impact:
            return "MED"
        else:
            return "LOW"
    
    def update_ticker(self):
        """Update ticker animation"""
        try:
            if len(self.ticker_text) > 50:
                # Animate ticker
                display_width = 80  # Characters to show
                
                if self.ticker_position >= len(self.ticker_text):
                    self.ticker_position = 0
                
                # Create scrolling text
                extended_text = self.ticker_text + " • " + self.ticker_text
                start_pos = self.ticker_position
                end_pos = start_pos + display_width
                
                display_text = extended_text[start_pos:end_pos]
                self.ticker_label.setText(display_text)
                
                # Advance position
                self.ticker_position += 1
            else:
                # Static display for short text
                self.ticker_label.setText(self.ticker_text)
                
        except Exception as e:
            print(f"Error updating ticker: {e}")