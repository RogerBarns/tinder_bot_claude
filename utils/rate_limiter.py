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