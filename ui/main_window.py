"""
Main application window with Bloomberg-style dark theme
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from typing import Dict, Any

from .panels import *
from .styles import get_dark_theme_stylesheet
from .region_selector import RegionSelector

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, engine, config):
        super().__init__()
        self.engine = engine
        self.config = config
        
        self.setWindowTitle("NQ Master v3 - Professional Trading Terminal")
        self.setGeometry(100, 100, config.window_width, config.window_height)
        
        # Set dark theme
        self.setStyleSheet(get_dark_theme_stylesheet())
        
        # Initialize components
        self.region_selector = RegionSelector()
        self.setup_ui()
        self.setup_connections()
        self.setup_timers()
        
        # Initial data update
        self.update_all_panels()
    
    def setup_ui(self):
        """Setup the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        # Create menu bar
        self.setup_menu_bar()
        
        # Create status bar
        self.setup_status_bar()
        
        # Create main content area
        content_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(content_splitter)
        
        # Left panel (60% width)
        left_panel = self.create_left_panel()
        content_splitter.addWidget(left_panel)
        
        # Right panel (40% width)
        right_panel = self.create_right_panel()
        content_splitter.addWidget(right_panel)
        
        # Set splitter proportions
        content_splitter.setStretchFactor(0, 60)
        content_splitter.setStretchFactor(1, 40)
        
    def create_left_panel(self) -> QWidget:
        """Create left panel with main trading info"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Price & Signal Panel (top)
        self.price_panel = PriceSignalPanel(self.engine, self.config)
        layout.addWidget(self.price_panel, 35)
        
        # Confluence Analysis Panel (middle)
        self.confluence_panel = ConfluencePanel(self.engine, self.config)
        layout.addWidget(self.confluence_panel, 35)
        
        # Chart Panel (bottom)
        self.chart_panel = ChartPanel(self.engine, self.config)
        layout.addWidget(self.chart_panel, 30)
        
        return panel
    
    def create_right_panel(self) -> QWidget:
        """Create right panel with secondary info"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Signal History Panel (top)
        self.history_panel = SignalHistoryPanel(self.engine, self.config)
        layout.addWidget(self.history_panel, 40)
        
        # News Panel (bottom)
        self.news_panel = NewsPanel(self.engine, self.config)
        layout.addWidget(self.news_panel, 60)
        
        return panel
    
    def setup_menu_bar(self):
        """Setup application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        settings_action = QAction('&Settings', self)
        settings_action.setShortcut('Ctrl+,')
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('E&xit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu('&View')
        
        refresh_action = QAction('&Refresh Data', self)
        refresh_action.setShortcut('F5')
        refresh_action.triggered.connect(self.force_refresh)
        view_menu.addAction(refresh_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('&Tools')
        
        auto_locate_action = QAction('&Auto-locate DOM', self)
        auto_locate_action.setShortcut('Ctrl+A')
        auto_locate_action.triggered.connect(self.auto_locate_dom)
        tools_menu.addAction(auto_locate_action)
        
        manual_select_action = QAction('&Manual DOM Selection', self)
        manual_select_action.setShortcut('Ctrl+M')
        manual_select_action.triggered.connect(self.manual_select_dom)
        tools_menu.addAction(manual_select_action)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        
        about_action = QAction('&About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        """Setup status bar"""
        self.status_bar = self.statusBar()
        
        # Connection status
        self.connection_label = QLabel("Connecting...")
        self.status_bar.addWidget(self.connection_label)
        
        # OCR status
        self.ocr_status_label = QLabel("OCR: Initializing")
        self.status_bar.addWidget(self.ocr_status_label)
        
        # Last update time
        self.last_update_label = QLabel("Last Update: --:--:--")
        self.status_bar.addPermanentWidget(self.last_update_label)
    
    def setup_connections(self):
        """Setup signal connections"""
        # Engine signals
        self.engine.price_updated.connect(self.on_price_updated)
        self.engine.signal_updated.connect(self.on_signal_updated)
        self.engine.confluence_updated.connect(self.on_confluence_updated)
        self.engine.news_updated.connect(self.on_news_updated)
        self.engine.error_occurred.connect(self.on_error_occurred)
    
    def setup_timers(self):
        """Setup update timers"""
        # Main update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_all_panels)
        self.update_timer.start(self.config.auto_refresh_ms)
        
        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)  # Update every second
    
    def update_all_panels(self):
        """Update all panels with latest data"""
        try:
            # Update each panel
            self.price_panel.update_data()
            self.confluence_panel.update_data()
            self.chart_panel.update_data()
            self.history_panel.update_data()
            self.news_panel.update_data()
            
        except Exception as e:
            print(f"Error updating panels: {e}")
    
    def update_status(self):
        """Update status bar"""
        from datetime import datetime
        
        # Update timestamp
        current_time = datetime.now().strftime("%H:%M:%S")
        self.last_update_label.setText(f"Last Update: {current_time}")
        
        # Update connection status
        data = self.engine.get_current_data()
        source = data.get("source", "NONE")
        
        if source == "OCR":
            self.connection_label.setText("Connected (Live OCR)")
            self.connection_label.setStyleSheet("color: #4CAF50;")  # Green
            self.ocr_status_label.setText("OCR: Active")
            self.ocr_status_label.setStyleSheet("color: #4CAF50;")
        elif source == "YAHOO":
            self.connection_label.setText("Connected (Yahoo)")
            self.connection_label.setStyleSheet("color: #FFC107;")  # Amber
            self.ocr_status_label.setText("OCR: Fallback")
            self.ocr_status_label.setStyleSheet("color: #FFC107;")
        else:
            self.connection_label.setText("Disconnected")
            self.connection_label.setStyleSheet("color: #F44336;")  # Red
            self.ocr_status_label.setText("OCR: Offline")
            self.ocr_status_label.setStyleSheet("color: #F44336;")
    
    # Event handlers
    def on_price_updated(self, price: float, source: str):
        """Handle price update"""
        pass  # Panels will update themselves
    
    def on_signal_updated(self, bias: str, confidence: int, reasons: list):
        """Handle signal update"""
        pass  # Panels will update themselves
    
    def on_confluence_updated(self, score: int, reasons: list):
        """Handle confluence update"""
        pass  # Panels will update themselves
    
    def on_news_updated(self, news_items: list):
        """Handle news update"""
        pass  # Panels will update themselves
    
    def on_error_occurred(self, error_msg: str):
        """Handle error"""
        self.status_bar.showMessage(f"Error: {error_msg}", 5000)
    
    # Menu actions
    def show_settings(self):
        """Show settings dialog"""
        # TODO: Implement settings dialog
        QMessageBox.information(self, "Settings", "Settings dialog coming soon!")
    
    def force_refresh(self):
        """Force data refresh"""
        self.update_all_panels()
        self.status_bar.showMessage("Data refreshed", 2000)
    
    def auto_locate_dom(self):
        """Auto-locate DOM region"""
        self.engine.auto_locate_dom()
        self.status_bar.showMessage("Auto-locating DOM...", 3000)
    
    def manual_select_dom(self):
        """Manual DOM region selection"""
        bbox = self.region_selector.select_region()
        if bbox:
            self.engine.set_dom_region(bbox)
            self.status_bar.showMessage(f"DOM region set: {bbox['width']}x{bbox['height']}", 3000)
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About NQ Master v3", 
                         "NQ Master v3\n"
                         "Professional Trading Terminal\n\n"
                         "Features:\n"
                         "• OCR + Yahoo Finance price fusion\n"
                         "• Real-time signal analysis\n"
                         "• Confluence scoring\n"
                         "• News integration\n\n"
                         "Version 3.0.0")
    
    def closeEvent(self, event):
        """Handle application close"""
        self.engine.stop()
        self.config.save()
        event.accept()