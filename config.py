"""
Configuration management for NQ Master v3
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class Config:
    """Application configuration settings"""
    
    # Trading Settings
    symbol: str = "NQ=F"
    yahoo_poll_sec: int = 10
    ocr_poll_sec: float = 0.25
    or_minutes: int = 15
    min_px: float = 2000.0
    max_px: float = 40000.0
    max_jump_pts: float = 60.0
    
    # OCR Settings
    ocr_psm: str = "6"
    search_right_px: int = 520
    bbox: Dict[str, int] = None
    
    # Audio/Visual Settings
    beeps_on: bool = True
    theme: str = "dark"
    
    # News Settings
    news_poll_sec: int = 30
    ff_json_url: str = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
    max_news_items: int = 40
    ticker_speed_chars_per_sec: float = 12.0
    
    # UI Settings
    window_width: int = 1400
    window_height: int = 900
    auto_refresh_ms: int = 250
    
    def __post_init__(self):
        if self.bbox is None:
            self.bbox = {"left": 1440, "top": 90, "width": 220, "height": 880}
    
    @classmethod
    def load(cls, config_path: str = "config.json") -> 'Config':
        """Load configuration from JSON file"""
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                return cls(**data)
            except Exception as e:
                print(f"Error loading config: {e}")
        return cls()
    
    def save(self, config_path: str = "config.json"):
        """Save configuration to JSON file"""
        try:
            with open(config_path, 'w') as f:
                json.dump(asdict(self), f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with fallback"""
        return getattr(self, key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        if hasattr(self, key):
            setattr(self, key, value)