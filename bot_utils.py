# utils/logger.py
"""
Centralized logging configuration
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Create logs directory
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


def setup_logging():
    """Configure application-wide logging"""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        LOG_DIR / "tinder_bot.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(console_formatter)
    root_logger.addHandler(file_handler)
    
    # Suppress noisy libraries
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('socketio').setLevel(logging.WARNING)
    logging.getLogger('engineio').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)


# utils/rate_limiter.py
"""
Rate limiting to avoid detection
"""
import time
import random
from typing import Dict


class RateLimiter:
    """Implements rate limiting with jitter"""
    
    def __init__(self):
        self.last_request_times: Dict[str, float] = {}
        self.min_interval = 3.0  # Minimum seconds between requests
        
    def wait_if_needed(self, endpoint: str = "default"):
        """Wait if necessary to respect rate limits"""
        now = time.time()
        last_time = self.last_request_times.get(endpoint, 0)
        
        time_passed = now - last_time
        if time_passed < self.min_interval:
            # Add jitter to avoid patterns
            wait_time = self.min_interval - time_passed + random.uniform(0, 1)
            time.sleep(wait_time)
        
        self.last_request_times[endpoint] = time.time()


# utils/stats.py
"""
Statistics tracking
"""
import json
from typing import Dict, Any
from pathlib import Path


class StatsManager:
    """Manages bot statistics"""
    
    def __init__(self):
        self.stats_file = Path(__file__).parent.parent / "data" / "bot_stats.json"
        self.stats = self._load_stats()
    
    def _load_stats(self) -> Dict[str, Any]:
        """Load stats from file"""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "total_likes": 0,
            "total_passes": 0,
            "total_matches": 0,
            "total_messages": 0,
            "total_approved": 0,
            "total_rejected": 0,
            "likes_attempted": 0,
            "matches_made": 0
        }
    
    def _save_stats(self):
        """Save stats to file"""
        self.stats_file.parent.mkdir(exist_ok=True)
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def increment(self, key: str, value: int = 1):
        """Increment a stat"""
        self.stats[key] = self.stats.get(key, 0) + value
        self._save_stats()
    
    def get(self, key: str, default: Any = 0) -> Any:
        """Get a stat value"""
        return self.stats.get(key, default)
    
    def get_all(self) -> Dict[str, Any]:
        """Get all stats"""
        return self.stats.copy()


# utils/data_manager.py
"""
Data persistence management
"""
import json
from typing import Set, Dict, Any
from pathlib import Path


class DataManager:
    """Manages persistent data"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        self.replied_file = self.data_dir / "replied_matches.json"
        self.rejected_file = self.data_dir / "rejected_matches.json"
        
        self.replied_messages = self._load_replied()
        self.rejected_matches = self._load_rejected()
    
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
    
    def has_replied_to(self, match_id: str, message_time: str) -> bool:
        """Check if we've replied to a specific message"""
        return self.replied_messages.get(match_id) == message_time
    
    def has_ever_replied_to(self, match_id: str) -> bool:
        """Check if we've ever replied to this match"""
        return match_id in self.replied_messages
    
    def mark_replied(self, match_id: str, message_time: str):
        """Mark a message as replied"""
        self.replied_messages[match_id] = message_time
        
        with open(self.replied_file, 'w') as f:
            json.dump(self.replied_messages, f)
    
    def is_rejected(self, match_id: str) -> bool:
        """Check if match was rejected"""
        return match_id in self.rejected_matches
    
    def mark_rejected(self, match_id: str):
        """Mark match as rejected"""
        self.rejected_matches.add(match_id)
        
        with open(self.rejected_file, 'w') as f:
            json.dump(list(self.rejected_matches), f)
