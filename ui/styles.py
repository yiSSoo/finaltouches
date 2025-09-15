"""
Bloomberg-style dark theme stylesheets
"""

def get_dark_theme_stylesheet() -> str:
    """Return the main dark theme stylesheet"""
    return """
/* Main window and base styling */
QMainWindow {
    background-color: #1E1E1E;
    color: #E0E0E0;
}

QWidget {
    background-color: #1E1E1E;
    color: #E0E0E0;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 9pt;
}

/* Panel styling */
QFrame {
    background-color: #2D2D2D;
    border: 1px solid #404040;
    border-radius: 6px;
    padding: 8px;
}

/* Headers and titles */
QLabel[class="header"] {
    font-size: 11pt;
    font-weight: bold;
    color: #FFFFFF;
    padding: 4px 0px;
}

QLabel[class="subheader"] {
    font-size: 10pt;
    font-weight: 600;
    color: #B0B0B0;
    padding: 2px 0px;
}

/* Price displays */
QLabel[class="price-large"] {
    font-size: 24pt;
    font-weight: bold;
    color: #FFFFFF;
    background-color: transparent;
}

QLabel[class="price-medium"] {
    font-size: 14pt;
    font-weight: 600;
    color: #E0E0E0;
}

/* Signal indicators */
QLabel[class="signal-bullish"] {
    background-color: #2E7D32;
    color: #FFFFFF;
    border-radius: 4px;
    padding: 6px 12px;
    font-weight: bold;
}

QLabel[class="signal-bearish"] {
    background-color: #C62828;
    color: #FFFFFF;
    border-radius: 4px;
    padding: 6px 12px;
    font-weight: bold;
}

QLabel[class="signal-neutral"] {
    background-color: #455A64;
    color: #FFFFFF;
    border-radius: 4px;
    padding: 6px 12px;
    font-weight: bold;
}

/* Tables */
QTableWidget {
    background-color: #252525;
    alternate-background-color: #2A2A2A;
    border: 1px solid #404040;
    gridline-color: #404040;
    border-radius: 4px;
}

QTableWidget::item {
    padding: 6px;
    border: none;
}

QTableWidget::item:selected {
    background-color: #1976D2;
    color: #FFFFFF;
}

QHeaderView::section {
    background-color: #353535;
    color: #E0E0E0;
    padding: 8px;
    border: none;
    border-right: 1px solid #404040;
    font-weight: 600;
}

QHeaderView::section:horizontal {
    border-bottom: 2px solid #1976D2;
}

/* Scroll bars */
QScrollBar:vertical {
    background-color: #2D2D2D;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #555555;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #666666;
}

/* Buttons */
QPushButton {
    background-color: #1976D2;
    color: #FFFFFF;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #1565C0;
}

QPushButton:pressed {
    background-color: #0D47A1;
}

QPushButton:disabled {
    background-color: #424242;
    color: #757575;
}

/* Menu bar */
QMenuBar {
    background-color: #252525;
    border-bottom: 1px solid #404040;
    padding: 2px;
}

QMenuBar::item {
    background-color: transparent;
    padding: 6px 12px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #1976D2;
}

QMenu {
    background-color: #2D2D2D;
    border: 1px solid #404040;
    border-radius: 4px;
    padding: 4px;
}

QMenu::item {
    padding: 6px 20px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #1976D2;
}

/* Status bar */
QStatusBar {
    background-color: #252525;
    border-top: 1px solid #404040;
    color: #B0B0B0;
}

QStatusBar QLabel {
    padding: 4px 8px;
}

/* Progress bars */
QProgressBar {
    background-color: #2D2D2D;
    border: 1px solid #404040;
    border-radius: 4px;
    text-align: center;
    color: #E0E0E0;
}

QProgressBar::chunk {
    background-color: #1976D2;
    border-radius: 3px;
}

/* Splitters */
QSplitter::handle {
    background-color: #404040;
}

QSplitter::handle:horizontal {
    width: 2px;
}

QSplitter::handle:vertical {
    height: 2px;
}

/* Text colors for different states */
.positive {
    color: #4CAF50;
    font-weight: 600;
}

.negative {
    color: #F44336;
    font-weight: 600;
}

.neutral {
    color: #E0E0E0;
}

.warning {
    color: #FFC107;
}

.info {
    color: #2196F3;
}

/* News ticker */
QLabel[class="news-ticker"] {
    background-color: #1565C0;
    color: #FFFFFF;
    padding: 4px 8px;
    border-radius: 2px;
    font-size: 8pt;
}

/* Chart background */
QFrame[class="chart"] {
    background-color: #1E1E1E;
    border: 1px solid #404040;
}
"""

def get_panel_stylesheet() -> str:
    """Panel-specific styling"""
    return """
QFrame[class="panel"] {
    background-color: #2D2D2D;
    border: 1px solid #404040;
    border-radius: 8px;
    padding: 12px;
    margin: 4px;
}

QFrame[class="panel-header"] {
    background-color: #353535;
    border: none;
    border-radius: 6px;
    padding: 8px;
    margin-bottom: 8px;
}
"""