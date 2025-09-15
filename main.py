#!/usr/bin/env python3
"""
NQ Master v3 - Desktop Trading Application
Professional PyQt-based GUI for NQ futures trading with OCR+Yahoo fusion
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon
from config import Config
from ui.main_window import MainWindow
from core.engine import TradingEngine

class NQMasterApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.setup_application()
        
        # Initialize core components
        self.config = Config()
        self.engine = TradingEngine(self.config)
        self.main_window = MainWindow(self.engine, self.config)
        
    def setup_application(self):
        """Configure application-wide settings"""
        self.app.setApplicationName("NQ Master v3")
        self.app.setApplicationVersion("3.0.0")
        self.app.setOrganizationName("NQ Master")
        
        # Set application icon if available
        if os.path.exists("assets/icon.ico"):
            self.app.setWindowIcon(QIcon("assets/icon.ico"))
        
        # Configure high DPI scaling
        self.app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        self.app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        # Set default font
        font = QFont("Segoe UI", 9)
        self.app.setFont(font)
        
    def run(self):
        """Start the application"""
        try:
            # Start the trading engine
            self.engine.start()
            
            # Show main window
            self.main_window.show()
            
            # Start event loop
            return self.app.exec_()
            
        except Exception as e:
            print(f"Error starting application: {e}")
            return 1
        finally:
            # Cleanup
            if hasattr(self, 'engine'):
                self.engine.stop()

def main():
    """Application entry point"""
    app = NQMasterApp()
    sys.exit(app.run())

if __name__ == "__main__":
    main()