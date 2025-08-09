"""
Human-like behavior simulation utilities
"""
import time
import random
import threading
from datetime import datetime, time as datetime_time
from typing import Callable, Optional, Tuple
import pytz

from config import HUMAN_DELAYS
from utils.logger import get_logger

logger = get_logger(__name__)


class HumanSchedule:
    """Simulates human daily patterns"""
    
    def __init__(self, timezone: str = "Europe/London"):
        self.timezone = pytz.timezone(timezone)
        self.sleep_start = datetime_time(1, 0)  # 1 AM
        self.sleep_end = datetime_time(6, 0)    # 6 AM
        self.peak_hours = [(18, 23), (12, 14)]  # Evening and lunch
        self.low_hours = [(2, 5), (9, 11)]      # Night and morning work
    
    def is_sleeping(self) -> bool:
        """Check if it's sleep time"""
        current_time = datetime.now(self.timezone).time()
        
        if self.sleep_start <= self.sleep_end:
            return self.sleep_start <= current_time <= self.sleep_end
        else:
            return current_time >= self.sleep_start or current_time <= self.sleep_end
    
    def get_activity_level(self) -> float:
        """Get current activity level (0.0 to 1.0)"""
        if self.is_sleeping():
            return 0.0
        
        current_hour = datetime.now(self.timezone).hour
        
        # Check peak hours
        for start, end in self.peak_hours:
            if start <= current_hour <= end:
                return random.uniform(0.8, 1.0)
        
        # Check low activity hours
        for start, end in self.low_hours:
            if start <= current_hour <= end:
                return random.uniform(0.2, 0.4)
        
        # Default moderate activity
        return random.uniform(0.4, 0.7)
    
    def should_take_break(self) -> bool:
        """Randomly decide if user should take a break"""
        activity = self.get_activity_level()
        
        # Lower activity = higher chance of break
        break_chance = 0.1 * (1.0 - activity)
        
        # Add randomness for weekends (assuming more breaks)
        if datetime.now(self.timezone).weekday() >= 5:  # Saturday/Sunday
            break_chance *= 1.5
        
        return random.random() < break_chance


# Global schedule instance
schedule = HumanSchedule()


def human_delay(min_seconds: float, max_seconds: float, activity_based: bool = True):
    """Sleep for a human-like random duration"""
    base_delay = random.uniform(min_seconds, max_seconds)
    
    if activity_based:
        # Adjust based on current activity level
        activity = schedule.get_activity_level()
        if activity == 0.0:  # Sleeping
            logger.info("😴 User is sleeping, skipping delay")
            return
        
        # Higher activity = shorter delays
        adjusted_delay = base_delay * (2.0 - activity)
    else:
        adjusted_delay = base_delay
    
    # Add micro-variations
    final_delay = adjusted_delay + random.uniform(-0.5, 0.5)
    final_delay = max(0.1, final_delay)  # Minimum 100ms
    
    logger.debug(f"Human delay: {final_delay:.1f}s")
    time.sleep(final_delay)


def simulate_typing(message: str, wpm: int = 40) -> float:
    """Calculate and simulate typing delay for a message"""
    # Average word length + spaces
    words = len(message.split())
    
    # Add variation to WPM (some people type faster/slower)
    actual_wpm = wpm + random.randint(-10, 10)
    actual_wpm = max(20, actual_wpm)  # Minimum 20 WPM
    
    # Base typing time
    typing_time = (words / actual_wpm) * 60
    
    # Add time for thinking/corrections
    thinking_pauses = words * random.uniform(0.1, 0.3)
    
    # Add random corrections (backspace and retype)
    correction_time = random.uniform(0, 2) if random.random() < 0.3 else 0
    
    total_time = typing_time + thinking_pauses + correction_time
    
    # Add small random variation
    total_time *= random.uniform(0.9, 1.1)
    
    logger.info(f"Typing '{message[:20]}...' will take {total_time:.1f}s")
    
    # Simulate with progress
    start_time = time.time()
    while time.time() - start_time < total_time:
        progress = (time.time() - start_time) / total_time
        chars_typed = int(len(message) * progress)
        print(f"\r💬 Typing... ({chars_typed}/{len(message)} chars)", end="", flush=True)
        time.sleep(0.1)
    
    print("\r" + " " * 50 + "\r", end="", flush=True)  # Clear line
    
    return total_time


def add_typo(text: str, typo_rate: float = 0.02) -> str:
    """Add realistic typos to text"""
    if not text or random.random() > typo_rate:
        return text
    
    typo_types = [
        "swap",      # Swap adjacent characters
        "double",    # Double a character
        "missing",   # Miss a character
        "neighbor",  # Hit neighboring key
    ]
    
    typo_type = random.choice(typo_types)
    
    # Find a suitable position (not first/last char, only letters)
    valid_positions = [
        i for i in range(1, len(text) - 1) 
        if text[i].isalpha()
    ]
    
    if not valid_positions:
        return text

def add_request_jitter(base_delay: float = 0.0) -> float:
    """Add random jitter to requests to avoid patterns"""
    jitter = random.uniform(-0.5, 2.0)
    return max(0.1, base_delay + jitter)