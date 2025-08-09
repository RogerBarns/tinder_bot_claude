"""
Central configuration management for Tinder Bot
Enhanced with browser API support and better validation
"""
import os
import json
import random
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
for directory in [DATA_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

# Environment variables
TINDER_AUTH_TOKEN = os.getenv("TINDER_AUTH_TOKEN")  # Optional for browser mode
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
MY_USER_ID = os.getenv("MY_USER_ID", "56c33d1c75f8e79e5702d7c9")

# File paths
CONFIG_FILE = DATA_DIR / "config.json"
STATS_FILE = DATA_DIR / "bot_stats.json"
REPLIED_FILE = DATA_DIR / "replied_matches.json"
REJECTED_FILE = DATA_DIR / "rejected_matches.json"
CHAT_LOG_FILE = DATA_DIR / "chat_log.jsonl"  # Changed to JSONL for better streaming
FULL_HISTORY_FILE = DATA_DIR / "full_history.jsonl"
AUTO_APPROVED_FILE = DATA_DIR / "auto_approved_log.jsonl"
CLAUDE_USAGE_FILE = DATA_DIR / "claude_usage.json"
SESSION_FILE = DATA_DIR / "browser_session.json"

# API endpoints (legacy - kept for potential fallback)
BASE_URL = "https://api.gotinder.com"
ENDPOINTS = {
    "updates": f"{BASE_URL}/v2/updates",
    "matches": f"{BASE_URL}/v2/matches",
    "recs": f"{BASE_URL}/v2/recs/core",
    "like": f"{BASE_URL}/like/{{user_id}}",
    "pass": f"{BASE_URL}/pass/{{user_id}}",
    "message": f"{BASE_URL}/user/matches/{{match_id}}",
    "meta": f"{BASE_URL}/meta",
}

# Default configuration with browser API support
DEFAULT_CONFIG = {
    # Core bot settings
    "bot_enabled": False,
    "use_browser_api": True,  # Primary API mode - browser automation
    "auto_approve": True,
    "auto_swipe": False,
    "test_mode": False,

    # Timing and limits
    "swipe_interval": 30,
    "match_limit": 100,
    "swipe_limit": 50,
    "message_delay_min": 30,
    "message_delay_max": 120,
    "typing_delay": 3,
    "rate_limit_interval": 3,
    "max_retries": 3,
    "concurrent_replies": 3,

    # AI settings
    "personality": "default",
    "max_tokens": 300,
    "temperature": 0.8,

    # Browser settings
    "browser_headless": False,  # Set to True for production
    "browser_viewport_width": 1366,
    "browser_viewport_height": 768,
    "browser_user_agent_rotation": True,
    "browser_proxy": None,  # Optional proxy setting
    "session_persistence": True,

    # Safety settings
    "respect_sleep_schedule": False,  # UK sleep hours 1-6 AM
    "max_daily_messages": 100,
    "max_daily_swipes": 200,
    "anti_detection_delays": True,

    # Logging
    "log_level": "INFO",
    "save_full_conversations": True,
    "save_screenshots": False,  # For debugging
}

# Human behavior ranges (in seconds) - Enhanced for browser automation
HUMAN_DELAYS = {
    # Typing simulation
    "typing_base": (2.0, 8.0),
    "typing_per_char": (0.05, 0.15),
    "typing_pause": (0.1, 0.5),

    # Between actions
    "between_messages": (20.0, 80.0),
    "between_swipes": (2.0, 8.0),
    "between_clicks": (0.5, 2.0),
    "page_load_wait": (1.0, 3.0),

    # Longer breaks for realism
    "short_break": (60, 180),      # 1-3 minutes
    "medium_break": (300, 600),    # 5-10 minutes
    "long_break": (900, 1800),     # 15-30 minutes
    "night_sleep": (6 * 3600, 8 * 3600),  # 6-8 hours
}

# Enhanced personality system
PERSONALITIES = {
    "default": {
        "name": "Josh",
        "age": 34,
        "location": "Grimsby",
        "occupation": "Software Developer",
        "traits": ["confident", "british", "flirty", "funny", "tech-savvy"],
        "interests": ["gym", "italian food", "cars", "technology", "travel"],
        "car": "blue modified 2005 Subaru Impreza WRX",
        "contact": {
            "snapchat": "Fruityfrogs",
            "whatsapp": "+447879906540"
        },
        "quirks": ["foot fetish (soles)", "car enthusiast", "gym 3x/week"],
        "system_prompt": """Your name is Josh. You're 34, confident, British, 5'10, seductive, and you're responding on Tinder.
You're an expert pickup artist who utilizes PUA methods like push-pull. You live in Grimsby, you're flirty and funny with chill energy.
Your snapchat is Fruityfrogs and your whatsapp is +447879906540 - only share when the conversation is going well.
You drive a blue modified 2005 Subaru Impreza WRX, enjoy food (especially Italian), and go to the gym 3x/week.
You're a software developer who loves technology. You have a foot fetish (soles) and love seeing photos of them.
Keep replies short (1-2 sentences max), sexy, human, and confident. Use British slang occasionally.
NEVER mention being AI or bot. No asterisk actions like *smiles*. Stay in character always.
Current time: {current_time} on {current_date}."""
    },
    "flirty": {
        "modifier": "Be extra flirty and suggestive while keeping it classy. Use more cheeky banter.",
        "traits": ["confident", "seductive", "cheeky", "playful"]
    },
    "funny": {
        "modifier": "Use humor and British wit to keep things light and entertaining. Make them laugh.",
        "traits": ["witty", "sarcastic", "playful", "entertaining"]
    },
    "gentle": {
        "modifier": "Be warm and respectful, making them feel special. Show genuine interest.",
        "traits": ["sweet", "kind", "genuine", "caring"]
    },
    "dominant": {
        "modifier": "Be more assertive and take charge of the conversation. Show leadership.",
        "traits": ["confident", "assertive", "leading", "decisive"]
    },
    "casual": {
        "modifier": "Keep things very relaxed and laid back. No pressure, just fun conversation.",
        "traits": ["relaxed", "easygoing", "friendly", "approachable"]
    }
}

# Browser automation settings
BROWSER_CONFIG = {
    "chrome_options": [
        "--no-first-run",
        "--no-service-autorun",
        "--password-store=basic",
        "--disable-blink-features=AutomationControlled",
        "--disable-extensions",
        "--disable-plugins-discovery",
        "--disable-web-security",
        "--allow-running-insecure-content",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage"
    ],

    "user_agents": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ],

    "viewports": [
        (1366, 768), (1920, 1080), (1440, 900), (1536, 864), (1280, 720)
    ],

    # CSS selectors for Tinder elements (updated for current UI)
    "selectors": {
        "login_button": "[data-testid='login-button'], .c1p6lbu0 button, button[aria-label*='Log in']",
        "phone_input": "[data-testid='phone-number-input'], input[type='tel']",
        "sms_code": "[data-testid='sms-code-input'], input[placeholder*='code']",
        "matches_tab": "[data-testid='matches-tab'], a[href*='messages']",
        "discovery_tab": "[data-testid='discovery-tab'], a[href*='app']",
        "match_card": "[data-testid='match-card'], .matchListItem",
        "message_input": "[data-testid='msg-input'], textarea[placeholder*='Type']",
        "send_button": "[data-testid='send-msg-btn'], button[aria-label*='Send']",
        "like_button": "[data-testid='like-button'], .recsCardboard__card button:last-child",
        "pass_button": "[data-testid='pass-button'], .recsCardboard__card button:first-child",
        "message_list": "[data-testid='message-list'], .messageList",
        "profile_card": ".recsCardboard__card, [data-testid='profile-card']"
    }
}

# Rate limiting and safety
SAFETY_LIMITS = {
    "max_actions_per_hour": 60,
    "max_messages_per_day": 100,
    "max_swipes_per_day": 200,
    "min_action_interval": 2,  # seconds
    "cooldown_after_error": 30,  # seconds
    "max_consecutive_errors": 5,
    "session_max_duration": 4 * 3600,  # 4 hours
    "mandatory_break_interval": 2 * 3600,  # 2 hours
}

# Sleep schedule (UK timezone)
SLEEP_SCHEDULE = {
    "start_hour": 1,   # 1 AM
    "end_hour": 6,     # 6 AM
    "timezone": "Europe/London"
}


class ConfigManager:
    """Enhanced configuration manager with validation and browser support"""

    def __init__(self):
        self._config = self._load_config()
        self._validate_config()
        self._ensure_files_exist()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    user_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    config = DEFAULT_CONFIG.copy()
                    config.update(user_config)
                    return config
            except Exception as e:
                print(f"⚠️ Error loading config: {e}, using defaults")

        # Create default config
        self._save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2, sort_keys=True)
        except Exception as e:
            print(f"⚠️ Error saving config: {e}")

    def _validate_config(self):
        """Validate configuration values"""
        # Ensure required API keys are present if needed
        if not self._config.get("use_browser_api", True):
            if not TINDER_AUTH_TOKEN:
                print("⚠️ TINDER_AUTH_TOKEN required for API mode")

        if not CLAUDE_API_KEY:
            print("❌ CLAUDE_API_KEY is required")

        # Validate numeric ranges
        numeric_validations = {
            "message_delay_min": (10, 300),
            "message_delay_max": (30, 600),
            "match_limit": (1, 500),
            "swipe_limit": (1, 500),
            "max_tokens": (50, 1000),
            "temperature": (0.0, 2.0)
        }

        for key, (min_val, max_val) in numeric_validations.items():
            value = self._config.get(key)
            if value is not None and not (min_val <= value <= max_val):
                print(f"⚠️ {key} value {value} outside valid range [{min_val}, {max_val}]")
                # Reset to default
                if key in DEFAULT_CONFIG:
                    self._config[key] = DEFAULT_CONFIG[key]

        # Validate personality exists
        personality = self._config.get("personality", "default")
        if personality not in PERSONALITIES:
            print(f"⚠️ Unknown personality '{personality}', using 'default'")
            self._config["personality"] = "default"

    def _ensure_files_exist(self):
        """Create necessary files if they don't exist"""
        file_templates = {
            REPLIED_FILE: {},
            STATS_FILE: {"total_messages": 0, "total_swipes": 0, "matches": 0},
            REJECTED_FILE: {},
            CLAUDE_USAGE_FILE: {"total_tokens": 0, "total_cost": 0.0}
        }

        for file_path, default_content in file_templates.items():
            if not file_path.exists():
                try:
                    with open(file_path, 'w') as f:
                        json.dump(default_content, f, indent=2)
                except Exception as e:
                    print(f"⚠️ Could not create {file_path}: {e}")

        # Create JSONL files
        jsonl_files = [CHAT_LOG_FILE, FULL_HISTORY_FILE, AUTO_APPROVED_FILE]
        for file_path in jsonl_files:
            if not file_path.exists():
                try:
                    file_path.touch()
                except Exception as e:
                    print(f"⚠️ Could not create {file_path}: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)

    def set(self, key: str, value: Any):
        """Set configuration value and save"""
        old_value = self._config.get(key)
        self._config[key] = value
        self._save_config(self._config)

        # Log important changes
        if key in ["bot_enabled", "use_browser_api", "auto_swipe"] and old_value != value:
            print(f"📝 Config changed: {key} = {value}")

    def update(self, updates: Dict[str, Any]):
        """Update multiple configuration values"""
        self._config.update(updates)
        self._save_config(self._config)

    def get_personality(self, personality_name: Optional[str] = None) -> Dict[str, Any]:
        """Get personality configuration"""
        name = personality_name or self._config.get("personality", "default")
        return PERSONALITIES.get(name, PERSONALITIES["default"])

    def get_random_user_agent(self) -> str:
        """Get random user agent for browser"""
        return random.choice(BROWSER_CONFIG["user_agents"])

    def get_random_viewport(self) -> tuple:
        """Get random viewport size"""
        return random.choice(BROWSER_CONFIG["viewports"])

    def get_human_delay(self, delay_type: str) -> float:
        """Get random human-like delay"""
        if delay_type in HUMAN_DELAYS:
            min_delay, max_delay = HUMAN_DELAYS[delay_type]
            return random.uniform(min_delay, max_delay)
        return 1.0

    def is_within_safety_limits(self, action_type: str, current_count: int) -> bool:
        """Check if action is within safety limits"""
        limits = {
            "messages": self.get("max_daily_messages", 100),
            "swipes": self.get("max_daily_swipes", 200)
        }

        limit = limits.get(action_type, float('inf'))
        return current_count < limit

    @property
    def all(self) -> Dict[str, Any]:
        """Get all configuration values"""
        return self._config.copy()

    def export_config(self, file_path: Optional[Path] = None) -> Dict[str, Any]:
        """Export current configuration"""
        export_data = {
            "config": self.all,
            "personalities": PERSONALITIES,
            "browser_config": BROWSER_CONFIG,
            "safety_limits": SAFETY_LIMITS,
            "exported_at": datetime.now().isoformat()
        }

        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(export_data, f, indent=2)
                print(f"✅ Configuration exported to {file_path}")
            except Exception as e:
                print(f"❌ Failed to export config: {e}")

        return export_data

    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self._config = DEFAULT_CONFIG.copy()
        self._save_config(self._config)
        print("🔄 Configuration reset to defaults")


# Global config instance
config = ConfigManager()

# Validation functions
def validate_environment() -> bool:
    """Validate required environment variables"""
    missing = []
    warnings = []

    if not CLAUDE_API_KEY:
        missing.append("CLAUDE_API_KEY")

    if not config.get("use_browser_api", True) and not TINDER_AUTH_TOKEN:
        missing.append("TINDER_AUTH_TOKEN (required for API mode)")

    if config.get("use_browser_api", True) and not TINDER_AUTH_TOKEN:
        warnings.append("TINDER_AUTH_TOKEN not set (OK for browser mode)")

    if missing:
        print(f"❌ Missing required environment variables:")
        for var in missing:
            print(f"   - {var}")
        return False

    if warnings:
        print(f"⚠️ Warnings:")
        for warning in warnings:
            print(f"   - {warning}")

    return True

def get_current_limits() -> Dict[str, Any]:
    """Get current safety limits and usage"""
    return {
        "safety_limits": SAFETY_LIMITS,
        "daily_limits": {
            "max_messages": config.get("max_daily_messages", 100),
            "max_swipes": config.get("max_daily_swipes", 200)
        },
        "delays": HUMAN_DELAYS,
        "browser_mode": config.get("use_browser_api", True)
    }


# Print config status on import (only if run directly)
if __name__ == "__main__":
    print("🔧 Tinder Bot Configuration")
    print("=" * 40)

    print(f"Mode: {'🌐 Browser Automation' if config.get('use_browser_api') else '🔌 API Mode'}")
    print(f"Bot Enabled: {'✅' if config.get('bot_enabled') else '❌'}")
    print(f"Personality: {config.get('personality', 'default')}")
    print(f"Test Mode: {'✅' if config.get('test_mode') else '❌'}")

    print(f"\nEnvironment:")
    print(f"  CLAUDE_API_KEY: {'✅ Set' if CLAUDE_API_KEY else '❌ Missing'}")
    print(f"  TINDER_AUTH_TOKEN: {'✅ Set' if TINDER_AUTH_TOKEN else '⚠️ Not set (OK for browser mode)'}")
    print(f"  MY_USER_ID: {MY_USER_ID}")

    print(f"\nFiles:")
    for file_path in [CONFIG_FILE, CHAT_LOG_FILE, REPLIED_FILE]:
        status = "✅" if file_path.exists() else "❌"
        print(f"  {file_path.name}: {status}")

    print(f"\nValidation: {'✅ Passed' if validate_environment() else '❌ Failed'}")