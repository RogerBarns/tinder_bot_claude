# utils/rate_limiter.py
"""
Rate limiting to avoid detection
"""
import time
import random
from typing import Dict
from threading import Lock


class RateLimiter:
    """Implements rate limiting with jitter"""
    
    def __init__(self, min_interval: float = 3.0):
        self.last_request_times: Dict[str, float] = {}
        self.min_interval = min_interval
        self._lock = Lock()
        
    def wait_if_needed(self, endpoint: str = "default"):
        """Wait if necessary to respect rate limits"""
        with self._lock:
            now = time.time()
            last_time = self.last_request_times.get(endpoint, 0)
            
            time_passed = now - last_time
            if time_passed < self.min_interval:
                # Add jitter to avoid patterns
                wait_time = self.min_interval - time_passed + random.uniform(0, 1)
                time.sleep(wait_time)
            
            self.last_request_times[endpoint] = time.time()
    
    def reset(self):
        """Reset all rate limit tracking"""
        with self._lock:
            self.last_request_times.clear()


# utils/stats.py
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
        with self._lock:
            self.stats["messages_sent_today"] = 0
            self.stats["last_reset"] = time.strftime("%Y-%m-%d")
            self._save_stats()


# utils/data_manager.py
"""
Data persistence management
"""
import json
from typing import Set, Dict, Any, List
from pathlib import Path
from threading import Lock


class DataManager:
    """Manages persistent data with thread safety"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        self.replied_file = self.data_dir / "replied_matches.json"
        self.rejected_file = self.data_dir / "rejected_matches.json"
        self.conversation_cache_file = self.data_dir / "conversation_cache.json"
        
        self.replied_messages = self._load_replied()
        self.rejected_matches = self._load_rejected()
        self.conversation_cache = self._load_conversation_cache()
        
        self._lock = Lock()
    
    def _load_replied(self) -> Dict[str, str]:
        """Load replied messages tracking"""
        if self.replied_file.exists():
            try:
                with open(self.replied_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _load_rejected(self) -> Set[str]:
        """Load rejected matches"""
        if self.rejected_file.exists():
            try:
                with open(self.rejected_file, 'r') as f:
                    return set(json.load(f))
            except:
                pass
        return set()
    
    def _load_conversation_cache(self) -> Dict[str, List[Dict]]:
        """Load conversation cache"""
        if self.conversation_cache_file.exists():
            try:
                with open(self.conversation_cache_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def has_replied_to(self, match_id: str, message_time: str) -> bool:
        """Check if we've replied to a specific message"""
        with self._lock:
            return self.replied_messages.get(match_id) == message_time
    
    def has_ever_replied_to(self, match_id: str) -> bool:
        """Check if we've ever replied to this match"""
        with self._lock:
            return match_id in self.replied_messages
    
    def mark_replied(self, match_id: str, message_time: str):
        """Mark a message as replied"""
        with self._lock:
            self.replied_messages[match_id] = message_time
            
            with open(self.replied_file, 'w') as f:
                json.dump(self.replied_messages, f)
    
    def is_rejected(self, match_id: str) -> bool:
        """Check if match was rejected"""
        with self._lock:
            return match_id in self.rejected_matches
    
    def mark_rejected(self, match_id: str):
        """Mark match as rejected"""
        with self._lock:
            self.rejected_matches.add(match_id)
            
            with open(self.rejected_file, 'w') as f:
                json.dump(list(self.rejected_matches), f)
    
    def remove_rejected(self, match_id: str):
        """Remove match from rejected list"""
        with self._lock:
            self.rejected_matches.discard(match_id)
            
            with open(self.rejected_file, 'w') as f:
                json.dump(list(self.rejected_matches), f)
    
    def cache_conversation(self, match_id: str, messages: List[Dict]):
        """Cache a conversation"""
        with self._lock:
            self.conversation_cache[match_id] = messages
            
            # Keep cache size reasonable (max 100 conversations)
            if len(self.conversation_cache) > 100:
                # Remove oldest entries
                oldest = sorted(self.conversation_cache.keys())[:20]
                for key in oldest:
                    del self.conversation_cache[key]
            
            with open(self.conversation_cache_file, 'w') as f:
                json.dump(self.conversation_cache, f)
    
    def get_cached_conversation(self, match_id: str) -> List[Dict]:
        """Get cached conversation"""
        with self._lock:
            return self.conversation_cache.get(match_id, [])
    
    def clear_all_data(self):
        """Clear all persistent data (use with caution)"""
        with self._lock:
            self.replied_messages.clear()
            self.rejected_matches.clear()
            self.conversation_cache.clear()
            
            # Save empty files
            with open(self.replied_file, 'w') as f:
                json.dump({}, f)
            with open(self.rejected_file, 'w') as f:
                json.dump([], f)
            with open(self.conversation_cache_file, 'w') as f:
                json.dump({}, f)


# utils/__init__.py
"""
Utility functions and helpers
"""
from .logger import setup_logging, get_logger, safe_log_info
from .rate_limiter import RateLimiter
from .stats import StatsManager
from .data_manager import DataManager
from .human_behavior import (
    HumanSchedule, schedule, human_delay, simulate_typing, 
    add_typo, add_request_jitter, should_sleep_now, random_sleep,
    queue_reply_later, estimate_typing_delay, inject_typo,
    is_suspicious_bio, push_log_to_dashboard
)

__all__ = [
    'setup_logging', 'get_logger', 'safe_log_info', 'RateLimiter', 'StatsManager',
    'DataManager', 'HumanSchedule', 'schedule', 'human_delay',
    'simulate_typing', 'add_typo', 'add_request_jitter', 'should_sleep_now',
    'random_sleep', 'queue_reply_later', 'estimate_typing_delay', 'inject_typo',
    'is_suspicious_bio', 'push_log_to_dashboard'
]
