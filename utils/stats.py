"""
Statistics tracking
"""
import json
from typing import Dict, Any
from pathlib import Path
from threading import Lock


class StatsManager:
    """Manages bot statistics with thread safety"""
    
    def __init__(self):
        self.stats_file = Path(__file__).parent.parent / "data" / "bot_stats.json"
        self.stats = self._load_stats()
        self._lock = Lock()
    
    def _load_stats(self) -> Dict[str, Any]:
        """Load stats from file"""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Default stats
        return {
            "total_likes": 0,
            "total_passes": 0,
            "total_matches": 0,
            "total_messages": 0,
            "total_approved": 0,
            "total_rejected": 0,
            "total_replied": 0,
            "likes_attempted": 0,
            "matches_made": 0,
            "swipe_sessions": 0,
            "messages_sent_today": 0,
            "last_reset": None
        }
    
    def _save_stats(self):
        """Save stats to file"""
        self.stats_file.parent.mkdir(exist_ok=True)
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def increment(self, key: str, value: int = 1):
        """Increment a stat"""
        with self._lock:
            self.stats[key] = self.stats.get(key, 0) + value
            self._save_stats()
    
    def set(self, key: str, value: Any):
        """Set a stat value"""
        with self._lock:
            self.stats[key] = value
            self._save_stats()
    
    def get(self, key: str, default: Any = 0) -> Any:
        """Get a stat value"""
        with self._lock:
            return self.stats.get(key, default)
    
    def get_all(self) -> Dict[str, Any]:
        """Get all stats"""
        with self._lock:
            return self.stats.copy()
    
    def reset_daily_stats(self):
        """Reset daily statistics"""
        import time
        with self._lock:
            self.stats["messages_sent_today"] = 0
            self.stats["last_reset"] = time.strftime("%Y-%m-%d")
            self._save_stats()