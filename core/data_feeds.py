"""
Data feed implementations for Yahoo Finance and OCR
"""

import time
import threading
import requests
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional, Dict

# OCR imports
import mss
import cv2
import pytesseract
import re

# Timezone
try:
    from zoneinfo import ZoneInfo
    ET = ZoneInfo("America/New_York")
except ImportError:
    from datetime import timezone
    ET = timezone(timedelta(hours=-5))

def now_et():
    return datetime.now(ET)

class YahooFeed:
    """Yahoo Finance data feed"""
    
    def __init__(self, config):
        self.config = config
        self._running = False
        self._stop_event = threading.Event()
        self.latest_data = None
        
    def start(self):
        """Start the Yahoo feed"""
        if self._running:
            return
        
        self._running = True
        self._stop_event.clear()
        
        self.feed_thread = threading.Thread(target=self._feed_loop, daemon=True)
        self.feed_thread.start()
    
    def stop(self):
        """Stop the Yahoo feed"""
        self._running = False
        self._stop_event.set()
    
    def get_latest_data(self) -> Optional[pd.DataFrame]:
        """Get the latest data"""
        return self.latest_data
    
    def _feed_loop(self):
        """Main feed loop"""
        while self._running and not self._stop_event.is_set():
            try:
                self._fetch_data()
            except Exception as e:
                print(f"Yahoo feed error: {e}")
            
            self._stop_event.wait(self.config.yahoo_poll_sec)
    
    def _fetch_data(self):
        """Fetch data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(self.config.symbol)
            data = ticker.history(period="1d", interval="1m", prepost=True)
            
            if data.empty:
                return
            
            # Clean and format data
            data = data.rename(columns=str.title)[["Open", "High", "Low", "Close", "Volume"]]
            data.index = data.index.tz_convert(ET)
            
            # Filter to current trading day
            today = now_et().date()
            data = data[data.index.date == today]
            
            self.latest_data = data
            
        except Exception as e:
            print(f"Error fetching Yahoo data: {e}")

class DOMLocator:
    """Auto-locator for TopstepX DOM price column"""
    
    PRICE_WORDS = {"PRICE", "PR1CE", "PRlCE", "PRlC", "RICE"}
    
    def __init__(self, config):
        self.config = config
    
    def auto_locate(self) -> Optional[Dict[str, int]]:
        """Automatically locate the price column in DOM"""
        try:
            with mss.mss() as sct:
                # Capture right side of screen where DOM typically appears
                monitor = sct.monitors[1]
                scan_width = min(self.config.search_right_px, monitor["width"])
                
                bbox = {
                    "left": monitor["left"] + monitor["width"] - scan_width,
                    "top": monitor["top"] + 50,
                    "width": scan_width,
                    "height": monitor["height"] - 100
                }
                
                img = np.array(sct.grab(bbox))
            
            # Process image for OCR
            gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 31, 2)
            
            # Run OCR to find text
            data = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DICT, config="--psm 6")
            
            # Look for "PRICE" header
            for i, text in enumerate(data["text"]):
                if not text:
                    continue
                
                text_upper = text.strip().upper()
                if text_upper in self.PRICE_WORDS:
                    # Found price header, create bbox below it
                    x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
                    
                    result_bbox = {
                        "left": max(0, bbox["left"] + x - 12),
                        "top": max(0, bbox["top"] + y + h + 6),
                        "width": 220,
                        "height": 880
                    }
                    return result_bbox
            
            # Fallback: look for numeric columns
            x_positions = []
            for i, text in enumerate(data["text"]):
                if text and re.search(r'\d', text.strip()):
                    x_positions.append(data["left"][i])
            
            if x_positions:
                # Use median x position of numeric text
                median_x = int(np.median(x_positions))
                result_bbox = {
                    "left": max(0, bbox["left"] + median_x - 40),
                    "top": bbox["top"] + 60,
                    "width": 220,
                    "height": bbox["height"] - 120
                }
                return result_bbox
            
            return None
            
        except Exception as e:
            print(f"Auto-locate error: {e}")
            return None

class OCRFeed:
    """OCR-based price feed from DOM"""
    
    PRICE_PATTERN = re.compile(r"(?<!\d)(\d{4,6}(?:\.\d{1,2})?)(?!\d)")
    
    def __init__(self, config):
        self.config = config
        self._running = False
        self._stop_event = threading.Event()
        
        self.bbox = dict(config.bbox)
        self.latest_price = None
        self.last_good_price = None
        self.last_ocr_time = None
        
        self.locator = DOMLocator(config)
        self.last_auto_locate = 0
    
    def start(self):
        """Start the OCR feed"""
        if self._running:
            return
        
        self._running = True
        self._stop_event.clear()
        
        self.ocr_thread = threading.Thread(target=self._ocr_loop, daemon=True)
        self.ocr_thread.start()
    
    def stop(self):
        """Stop the OCR feed"""
        self._running = False
        self._stop_event.set()
    
    def get_latest_price(self) -> Optional[float]:
        """Get the latest OCR price"""
        return self.latest_price
    
    def set_bbox(self, bbox: Dict[str, int]):
        """Set the OCR bounding box"""
        self.bbox = dict(bbox)
    
    def auto_locate(self):
        """Trigger auto-location of DOM"""
        try:
            new_bbox = self.locator.auto_locate()
            if new_bbox:
                self.set_bbox(new_bbox)
                print(f"Auto-located DOM at: {new_bbox}")
        except Exception as e:
            print(f"Auto-locate failed: {e}")
    
    def _ocr_loop(self):
        """Main OCR processing loop"""
        # Try auto-locate on startup
        self.auto_locate()
        
        while self._running and not self._stop_event.is_set():
            try:
                # Periodic auto-locate
                current_time = time.time()
                if current_time - self.last_auto_locate > 30:  # Every 30 seconds
                    if not self.last_ocr_time or (current_time - self.last_ocr_time) > 3:
                        self.auto_locate()
                    self.last_auto_locate = current_time
                
                # Capture and process
                price = self._capture_price()
                if price is not None:
                    self.latest_price = price
                    self.last_ocr_time = current_time
                
            except Exception as e:
                print(f"OCR loop error: {e}")
            
            self._stop_event.wait(self.config.ocr_poll_sec)
    
    def _capture_price(self) -> Optional[float]:
        """Capture and extract price from DOM"""
        try:
            # Screen capture
            with mss.mss() as sct:
                img = np.array(sct.grab(self.bbox))
            
            # Process image
            gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 31, 2)
            
            # OCR
            data = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DICT, config=f"--psm {self.config.ocr_psm}")
            
            # Extract prices
            prices = []
            for text in data["text"]:
                if not text:
                    continue
                
                clean_text = text.strip().replace(",", "")
                match = self.PRICE_PATTERN.search(clean_text)
                
                if match:
                    try:
                        price = float(match.group(1))
                        if self.config.min_px <= price <= self.config.max_px:
                            # Snap to NQ tick size (0.25)
                            price = round(price * 4) / 4
                            prices.append(price)
                    except ValueError:
                        continue
            
            if not prices:
                return None
            
            # Use median price to filter outliers
            median_price = float(np.median(prices))
            
            # Sanity check against last known good price
            if self.last_good_price is not None:
                if abs(median_price - self.last_good_price) > self.config.max_jump_pts:
                    return self.last_good_price
            
            self.last_good_price = median_price
            return median_price
            
        except Exception as e:
            print(f"OCR capture error: {e}")
            return None