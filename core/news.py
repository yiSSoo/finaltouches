"""
News feed integration for market context
"""

import time
import threading
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Timezone
try:
    from zoneinfo import ZoneInfo
    ET = ZoneInfo("America/New_York")
except ImportError:
    from datetime import timezone
    ET = timezone(timedelta(hours=-5))

def now_et():
    return datetime.now(ET)

class NewsFeed:
    """ForexFactory news feed integration"""
    
    def __init__(self, config):
        self.config = config
        self._running = False
        self._stop_event = threading.Event()
        
        self.news_items = []
        self.last_update = 0
        
        # Bearish keywords for market sentiment
        self.bearish_keywords = [
            "inflation", "hawkish", "rate hike", "unemployment low", 
            "cpi higher", "hot inflation", "fed hawkish", "rates higher",
            "tightening", "contractionary", "bear", "recession", "downturn"
        ]
        
    def start(self):
        """Start news feed"""
        if self._running:
            return
        
        self._running = True
        self._stop_event.clear()
        
        self.news_thread = threading.Thread(target=self._news_loop, daemon=True)
        self.news_thread.start()
    
    def stop(self):
        """Stop news feed"""
        self._running = False
        self._stop_event.set()
    
    def get_news_items(self) -> List[Dict]:
        """Get current news items"""
        return self.news_items.copy()
    
    def get_market_sentiment(self) -> str:
        """Analyze recent news for market sentiment"""
        if not self.news_items:
            return "NEUTRAL"
        
        # Check recent high-impact news
        recent_news = [item for item in self.news_items[:10]]
        bearish_count = 0
        
        for item in recent_news:
            title_lower = item.get("title", "").lower()
            impact = item.get("impact", "")
            
            # Weight high-impact news more heavily
            weight = 2 if "High" in impact else 1
            
            if any(keyword in title_lower for keyword in self.bearish_keywords):
                bearish_count += weight
        
        if bearish_count >= 3:
            return "BEARISH"
        elif bearish_count <= 1:
            return "BULLISH"
        else:
            return "NEUTRAL"
    
    def _news_loop(self):
        """Main news fetching loop"""
        while self._running and not self._stop_event.is_set():
            try:
                current_time = time.time()
                if current_time - self.last_update > self.config.news_poll_sec:
                    self._fetch_news()
                    self.last_update = current_time
                    
            except Exception as e:
                print(f"News feed error: {e}")
            
            self._stop_event.wait(5)  # Check every 5 seconds
    
    def _fetch_news(self):
        """Fetch news from ForexFactory"""
        try:
            response = requests.get(self.config.ff_json_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            news_items = []
            
            for event in data:
                title = event.get("title") or event.get("event") or ""
                if not title:
                    continue
                
                impact = (event.get("impact") or "").strip()
                date_str = event.get("date") or ""
                time_str = event.get("time") or ""
                country = event.get("country") or ""
                
                # Parse datetime
                try:
                    if date_str and time_str:
                        event_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
                        event_dt = event_dt.replace(tzinfo=ET)
                    else:
                        event_dt = now_et()
                except:
                    event_dt = now_et()
                
                news_item = {
                    "time": event_dt,
                    "title": title,
                    "impact": impact,
                    "country": country,
                    "actual": event.get("actual", ""),
                    "forecast": event.get("forecast", ""),
                    "previous": event.get("previous", "")
                }
                
                news_items.append(news_item)
            
            # Sort by time (newest first) and limit
            news_items.sort(key=lambda x: x["time"], reverse=True)
            self.news_items = news_items[:self.config.max_news_items]
            
        except Exception as e:
            print(f"Error fetching news: {e}")