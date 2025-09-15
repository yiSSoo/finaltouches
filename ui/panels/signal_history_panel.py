"""
Signal History Panel - Shows recent signal changes and performance
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime, timedelta

class SignalHistoryPanel(QFrame):
    """Panel showing signal history and changes"""
    
    def __init__(self, engine, config):
        super().__init__()
        self.engine = engine
        self.config = config
        
        self.setProperty("class", "panel")
        self.signal_history = []  # Store signal changes
        self.last_signal = None
        self.last_check_time = datetime.now()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Header
        header = QLabel("SIGNAL HISTORY")
        header.setProperty("class", "header")
        layout.addWidget(header)
        
        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["Time", "Signal", "Confidence", "Key Reason"])
        
        # Configure table
        header_view = self.history_table.horizontalHeader()
        header_view.setStretchLastSection(True)
        header_view.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setMaximumHeight(200)
        
        layout.addWidget(self.history_table)
        
        # Statistics section
        stats_frame = QFrame()
        stats_layout = QVBoxLayout(stats_frame)
        stats_layout.setContentsMargins(0, 8, 0, 0)
        
        stats_header = QLabel("SESSION STATS")
        stats_header.setProperty("class", "subheader")
        stats_layout.addWidget(stats_header)
        
        # Stats grid
        stats_grid = QGridLayout()
        stats_grid.setHorizontalSpacing(16)
        stats_grid.setVerticalSpacing(4)
        
        stats_grid.addWidget(QLabel("Signals Today:"), 0, 0)
        self.signals_count_label = QLabel("0")
        stats_grid.addWidget(self.signals_count_label, 0, 1)
        
        stats_grid.addWidget(QLabel("Bullish:"), 1, 0)
        self.bullish_count_label = QLabel("0")
        self.bullish_count_label.setStyleSheet("color: #4CAF50;")
        stats_grid.addWidget(self.bullish_count_label, 1, 1)
        
        stats_grid.addWidget(QLabel("Bearish:"), 1, 2)
        self.bearish_count_label = QLabel("0")
        self.bearish_count_label.setStyleSheet("color: #F44336;")
        stats_grid.addWidget(self.bearish_count_label, 1, 3)
        
        stats_grid.addWidget(QLabel("Last Change:"), 2, 0)
        self.last_change_label = QLabel("--")
        stats_grid.addWidget(self.last_change_label, 2, 1, 1, 3)
        
        stats_layout.addLayout(stats_grid)
        layout.addWidget(stats_frame)
        
        layout.addStretch()
    
    def update_data(self):
        """Update panel with latest signal data"""
        try:
            current_data = self.engine.get_current_data()
            current_time = datetime.now()
            
            current_signal = current_data.get("bias", "NEUTRAL")
            current_confidence = current_data.get("confidence", 50)
            current_reasons = current_data.get("reasons", [])
            
            # Check for signal change
            if self.last_signal != current_signal:
                if self.last_signal is not None:  # Don't record initial state
                    # Record signal change
                    key_reason = current_reasons[0] if current_reasons else "No reason given"
                    
                    self.signal_history.append({
                        "time": current_time,
                        "signal": current_signal,
                        "confidence": current_confidence,
                        "reason": key_reason
                    })
                    
                    # Limit history to last 50 entries
                    if len(self.signal_history) > 50:
                        self.signal_history = self.signal_history[-50:]
                
                self.last_signal = current_signal
                self._update_history_table()
            
            self._update_statistics()
            
        except Exception as e:
            print(f"Error updating signal history: {e}")
    
    def _update_history_table(self):
        """Update the history table with latest data"""
        try:
            # Clear and populate table
            self.history_table.setRowCount(len(self.signal_history))
            
            for i, entry in enumerate(reversed(self.signal_history)):  # Most recent first
                time_str = entry["time"].strftime("%H:%M:%S")
                signal = entry["signal"]
                confidence = f"{entry['confidence']}%"
                reason = entry["reason"][:50] + "..." if len(entry["reason"]) > 50 else entry["reason"]
                
                # Time
                time_item = QTableWidgetItem(time_str)
                time_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.history_table.setItem(i, 0, time_item)
                
                # Signal with color coding
                signal_item = QTableWidgetItem(signal)
                signal_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                
                if signal == "BULLISH":
                    signal_item.setForeground(QColor("#4CAF50"))
                elif signal == "BEARISH":
                    signal_item.setForeground(QColor("#F44336"))
                else:
                    signal_item.setForeground(QColor("#E0E0E0"))
                
                self.history_table.setItem(i, 1, signal_item)
                
                # Confidence
                confidence_item = QTableWidgetItem(confidence)
                confidence_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.history_table.setItem(i, 2, confidence_item)
                
                # Reason
                reason_item = QTableWidgetItem(reason)
                reason_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                reason_item.setToolTip(entry["reason"])  # Full reason in tooltip
                self.history_table.setItem(i, 3, reason_item)
                
        except Exception as e:
            print(f"Error updating history table: {e}")
    
    def _update_statistics(self):
        """Update session statistics"""
        try:
            # Count signals by type (today only)
            today = datetime.now().date()
            today_signals = [s for s in self.signal_history if s["time"].date() == today]
            
            total_signals = len(today_signals)
            bullish_count = len([s for s in today_signals if s["signal"] == "BULLISH"])
            bearish_count = len([s for s in today_signals if s["signal"] == "BEARISH"])
            
            self.signals_count_label.setText(str(total_signals))
            self.bullish_count_label.setText(str(bullish_count))
            self.bearish_count_label.setText(str(bearish_count))
            
            # Last change time
            if self.signal_history:
                last_change = self.signal_history[-1]["time"]
                time_diff = datetime.now() - last_change
                
                if time_diff.total_seconds() < 60:
                    self.last_change_label.setText(f"{int(time_diff.total_seconds())}s ago")
                elif time_diff.total_seconds() < 3600:
                    self.last_change_label.setText(f"{int(time_diff.total_seconds() // 60)}m ago")
                else:
                    self.last_change_label.setText(last_change.strftime("%H:%M"))
            else:
                self.last_change_label.setText("--")
                
        except Exception as e:
            print(f"Error updating statistics: {e}")