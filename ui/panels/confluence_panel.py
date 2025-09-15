"""
Confluence Analysis Panel - Shows weighted signal analysis
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class ConfluencePanel(QFrame):
    """Panel showing confluence analysis and reasoning"""
    
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
        header = QLabel("CONFLUENCE ANALYSIS")
        header.setProperty("class", "header")
        layout.addWidget(header)
        
        # Score section
        score_frame = QFrame()
        score_layout = QVBoxLayout(score_frame)
        score_layout.setContentsMargins(0, 8, 0, 8)
        
        # Score display
        score_container = QHBoxLayout()
        score_container.setAlignment(Qt.AlignCenter)
        
        score_container.addWidget(QLabel("Confluence Score:"))
        
        self.score_label = QLabel("50/100")
        self.score_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #E0E0E0;")
        score_container.addWidget(self.score_label)
        
        score_layout.addLayout(score_container)
        
        # Progress bar for visual representation
        self.score_progress = QProgressBar()
        self.score_progress.setRange(0, 100)
        self.score_progress.setValue(50)
        self.score_progress.setTextVisible(False)
        self.score_progress.setFixedHeight(12)
        score_layout.addWidget(self.score_progress)
        
        # Score interpretation
        self.score_interpretation = QLabel("NEUTRAL BIAS")
        self.score_interpretation.setAlignment(Qt.AlignCenter)
        self.score_interpretation.setStyleSheet("font-size: 11pt; font-weight: 600; color: #E0E0E0; padding: 4px;")
        score_layout.addWidget(self.score_interpretation)
        
        layout.addWidget(score_frame)
        
        # Reasoning section
        reasoning_header = QLabel("CONTRIBUTING FACTORS")
        reasoning_header.setProperty("class", "subheader")
        layout.addWidget(reasoning_header)
        
        # Scrollable reasons list
        self.reasons_widget = QTextEdit()
        self.reasons_widget.setReadOnly(True)
        self.reasons_widget.setMaximumHeight(200)
        self.reasons_widget.setStyleSheet("""
            QTextEdit {
                background-color: #252525;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 8px;
                font-size: 9pt;
                line-height: 1.4;
            }
        """)
        layout.addWidget(self.reasons_widget)
        
        layout.addStretch()
    
    def update_data(self):
        """Update panel with latest confluence analysis"""
        try:
            score, reasons = self.engine.get_confluence_analysis()
            
            # Update score display
            self.score_label.setText(f"{score}/100")
            self.score_progress.setValue(score)
            
            # Update score styling and interpretation
            if score >= 70:
                # Strong bearish
                self.score_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #F44336;")
                self.score_progress.setStyleSheet("QProgressBar::chunk { background-color: #F44336; }")
                self.score_interpretation.setText("STRONG BEARISH BIAS")
                self.score_interpretation.setStyleSheet("font-size: 11pt; font-weight: 600; color: #F44336; padding: 4px;")
                
            elif score >= 60:
                # Moderate bearish
                self.score_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #FF7043;")
                self.score_progress.setStyleSheet("QProgressBar::chunk { background-color: #FF7043; }")
                self.score_interpretation.setText("MODERATE BEARISH")
                self.score_interpretation.setStyleSheet("font-size: 11pt; font-weight: 600; color: #FF7043; padding: 4px;")
                
            elif score <= 30:
                # Strong bullish
                self.score_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #4CAF50;")
                self.score_progress.setStyleSheet("QProgressBar::chunk { background-color: #4CAF50; }")
                self.score_interpretation.setText("STRONG BULLISH BIAS")
                self.score_interpretation.setStyleSheet("font-size: 11pt; font-weight: 600; color: #4CAF50; padding: 4px;")
                
            elif score <= 40:
                # Moderate bullish
                self.score_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #66BB6A;")
                self.score_progress.setStyleSheet("QProgressBar::chunk { background-color: #66BB6A; }")
                self.score_interpretation.setText("MODERATE BULLISH")
                self.score_interpretation.setStyleSheet("font-size: 11pt; font-weight: 600; color: #66BB6A; padding: 4px;")
                
            else:
                # Neutral
                self.score_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #E0E0E0;")
                self.score_progress.setStyleSheet("QProgressBar::chunk { background-color: #1976D2; }")
                self.score_interpretation.setText("NEUTRAL BIAS")
                self.score_interpretation.setStyleSheet("font-size: 11pt; font-weight: 600; color: #E0E0E0; padding: 4px;")
            
            # Update reasons
            if reasons:
                reasons_html = self._format_reasons_html(reasons)
                self.reasons_widget.setHtml(reasons_html)
            else:
                self.reasons_widget.setPlainText("No confluence factors available")
                
        except Exception as e:
            print(f"Error updating confluence panel: {e}")
            self.score_label.setText("--/100")
            self.reasons_widget.setPlainText(f"Error: {e}")
    
    def _format_reasons_html(self, reasons):
        """Format reasons as HTML for better display"""
        html = "<div style='color: #E0E0E0; line-height: 1.5;'>"
        
        for i, reason in enumerate(reasons, 1):
            # Color code based on keywords
            color = "#E0E0E0"  # Default
            
            reason_lower = reason.lower()
            if any(word in reason_lower for word in ["bear", "short", "down", "below", "break"]):
                color = "#FF7043"  # Orange for bearish
            elif any(word in reason_lower for word in ["bull", "long", "up", "above", "oversold"]):
                color = "#66BB6A"  # Green for bullish
            elif "overbought" in reason_lower or "rsi>70" in reason_lower:
                color = "#F44336"  # Red for overbought
            
            html += f"<div style='margin: 2px 0; color: {color};'>"
            html += f"<span style='color: #B0B0B0;'>•</span> {reason}"
            html += "</div>"
        
        html += "</div>"
        return html