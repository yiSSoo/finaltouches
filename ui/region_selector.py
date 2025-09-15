"""
DOM Region Selector - Manual selection of OCR region
"""

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class RegionSelector:
    """Tool for manually selecting DOM region"""
    
    def __init__(self):
        self.selected_region = None
    
    def select_region(self):
        """Show region selection overlay"""
        try:
            # Create fullscreen overlay
            self.overlay = RegionOverlay()
            self.overlay.region_selected.connect(self._on_region_selected)
            self.overlay.show()
            
            # Wait for selection
            loop = QEventLoop()
            self.overlay.region_selected.connect(loop.quit)
            self.overlay.selection_cancelled.connect(loop.quit)
            loop.exec_()
            
            return self.selected_region
            
        except Exception as e:
            print(f"Error in region selection: {e}")
            return None
    
    def _on_region_selected(self, bbox):
        """Handle region selection"""
        self.selected_region = bbox

class RegionOverlay(QWidget):
    """Fullscreen overlay for region selection"""
    
    region_selected = pyqtSignal(dict)
    selection_cancelled = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setWindowState(Qt.WindowFullScreen)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Selection state
        self.selecting = False
        self.start_pos = QPoint()
        self.end_pos = QPoint()
        
        # Styling
        self.setStyleSheet("background-color: rgba(0, 0, 0, 50);")
        self.setCursor(Qt.CrossCursor)
        
        # Instructions
        self.instruction_label = QLabel("Drag to select DOM price area. Press ESC to cancel.", self)
        self.instruction_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(0, 0, 0, 180);
                padding: 10px;
                border-radius: 5px;
                font-size: 14pt;
            }
        """)
        self.instruction_label.adjustSize()
        
        # Position instructions at top center
        screen_geometry = QApplication.desktop().screenGeometry()
        label_x = (screen_geometry.width() - self.instruction_label.width()) // 2
        self.instruction_label.move(label_x, 50)
    
    def mousePressEvent(self, event):
        """Start selection"""
        if event.button() == Qt.LeftButton:
            self.selecting = True
            self.start_pos = event.pos()
            self.end_pos = event.pos()
            self.update()
    
    def mouseMoveEvent(self, event):
        """Update selection"""
        if self.selecting:
            self.end_pos = event.pos()
            self.update()
    
    def mouseReleaseEvent(self, event):
        """End selection"""
        if event.button() == Qt.LeftButton and self.selecting:
            self.selecting = False
            
            # Calculate selection rectangle
            x1, y1 = self.start_pos.x(), self.start_pos.y()
            x2, y2 = self.end_pos.x(), self.end_pos.y()
            
            left = min(x1, x2)
            top = min(y1, y2)
            width = abs(x2 - x1)
            height = abs(y2 - y1)
            
            # Validate selection
            if width > 20 and height > 20:
                bbox = {
                    "left": left,
                    "top": top,
                    "width": width,
                    "height": height
                }
                self.region_selected.emit(bbox)
            else:
                self.selection_cancelled.emit()
            
            self.close()
    
    def keyPressEvent(self, event):
        """Handle key press"""
        if event.key() == Qt.Key_Escape:
            self.selection_cancelled.emit()
            self.close()
        else:
            super().keyPressEvent(event)
    
    def paintEvent(self, event):
        """Draw selection rectangle"""
        painter = QPainter(self)
        
        if self.selecting:
            # Draw selection rectangle
            rect = QRect(self.start_pos, self.end_pos).normalized()
            
            # Semi-transparent overlay outside selection
            overlay_brush = QBrush(QColor(0, 0, 0, 100))
            painter.fillRect(self.rect(), overlay_brush)
            
            # Clear selection area
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.fillRect(rect, QColor(0, 0, 0, 0))
            
            # Draw selection border
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            pen = QPen(QColor(255, 255, 255, 200), 2, Qt.SolidLine)
            painter.setPen(pen)
            painter.drawRect(rect)
            
            # Draw size info
            size_text = f"{rect.width()} x {rect.height()}"
            text_rect = QRect(rect.bottomLeft() + QPoint(5, 5), QSize(100, 20))
            
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            painter.drawText(text_rect, Qt.AlignLeft, size_text)