"""
core/api_selector.py - Fixed API selector that returns the correct client
"""
import logging
from typing import Optional
from config import config

logger = logging.getLogger(__name__)


def get_api_client(context: str = "main"):
    """
    Get the appropriate API client based on configuration

    Args:
        context: Usage context (main, test, etc.)

    Returns:
        API client instance
    """
    use_browser = config.get("use_browser_api", True)
    test_mode = config.get("test_mode", False)

    logger.info(f"🔧 Getting API client (browser={use_browser}, test={test_mode}, context={context})")

    try:
        if use_browser:
            try:
                # Import the complete browser client
                from core.api_client import TinderAPIClient
                client = TinderAPIClient(config.all)
                logger.info("✅ Using Browser TinderAPIClient")
                return client
            except ImportError as e:
                logger.warning(f"⚠️ BrowserAPIClient not available: {e}")
                logger.info("📌 Falling back to stub client")

        # If browser mode disabled or failed, try API client
        try:
            from core.tinder_api import TinderAPIClient
            client = TinderAPIClient(config.all)
            logger.info(f"✅ Using API TinderAPIClient (test_mode={test_mode})")
            return client
        except ImportError:
            logger.warning("⚠️ API client not available")

        # Fallback to stub
        logger.info("🔄 Creating emergency stub client")
        return _get_stub_client("emergency")

    except Exception as e:
        logger.error(f"❌ Failed to create API client: {e}")
        logger.info("🔄 Creating emergency stub client")
        return _get_stub_client("emergency")


def _get_stub_client(account_id: str):
    """Return a stub client for testing when real clients aren't available"""

    class StubTinderAPIClient:
        """Stub client that logs actions but doesn't perform them"""

        def __init__(self, account_id: str = "main"):
            self.account_id = account_id
            self.is_logged_in = False
            logger.info(f"🤖 Stub API Client initialized for account: {account_id}")
            logger.warning("⚠️ This is a stub client - no real Tinder interactions will occur")

        def initialize_driver(self):
            logger.info("🔧 [STUB] Driver initialized")
            return True

        def login(self) -> bool:
            logger.info("🔑 [STUB] Login successful")
            self.is_logged_in = True
            return True

        def get_matches(self, limit: int = 100, messages_only: bool = False) -> list:
            logger.info(f"📋 [STUB] Getting {limit} matches (messages_only: {messages_only})")
            return [
                {
                    "match_id": "stub_match_1",
                    "name": "Test User 1",
                    "bio": "This is a test bio for testing the bot",
                    "messages": [
                        {
                            "id": "msg_1",
                            "role": "user",
                            "content": "Hey! How's your day going?",
                            "timestamp": "2025-08-07T20:00:00Z"
                        }
                    ]
                },
                {
                    "match_id": "stub_match_2",
                    "name": "Test User 2",
                    "bio": "Love hiking and coffee ☕",
                    "messages": [
                        {
                            "id": "msg_2",
                            "role": "user",
                            "content": "Nice photos! Do you travel much?",
                            "timestamp": "2025-08-07T21:00:00Z"
                        }
                    ]
                }
            ]

        def get_messages(self, match_id: str) -> list:
            logger.info(f"📬 [STUB] Getting messages for match: {match_id}")
            from datetime import datetime
            return [
                {
                    "id": "msg_1",
                    "role": "user",
                    "content": "Hey there!",
                    "timestamp": datetime.now().isoformat(),
                    "from_user": True
                },
                {
                    "id": "msg_2",
                    "role": "assistant",
                    "content": "Hi! How are you doing?",
                    "timestamp": datetime.now().isoformat(),
                    "from_user": False
                }
            ]

        def send_message(self, match_id: str, message: str) -> bool:
            logger.info(f"📤 [STUB] Sending message to {match_id}: {message}")
            return True

        def swipe_right(self) -> bool:
            logger.info("👍 [STUB] Swiped right")
            return True

        def swipe_left(self) -> bool:
            logger.info("👎 [STUB] Swiped left")
            return True

        def get_recommendations(self, limit: int = 10) -> list:
            logger.info(f"🔍 [STUB] Getting {limit} recommendations")
            return [
                {
                    "user_id": "stub_rec_1",
                    "name": "Test Profile 1",
                    "age": 25,
                    "bio": "Love traveling and good coffee",
                    "distance": 5,
                    "photos": []
                },
                {
                    "user_id": "stub_rec_2",
                    "name": "Test Profile 2",
                    "age": 28,
                    "bio": "Hiking enthusiast and dog lover",
                    "distance": 12,
                    "photos": []
                }
            ]

        def cleanup(self):
            logger.info("🧹 [STUB] Cleanup completed")

    return StubTinderAPIClient(account_id)


def check_dependencies() -> dict:
    """Check which dependencies are available"""
    deps = {
        "browser": False,
        "api": False,
        "missing": []
    }

    try:
        import undetected_chromedriver
        import selenium
        deps["browser"] = True
    except ImportError:
        deps["missing"].append("Browser: undetected-chromedriver, selenium")

    try:
        import requests
        deps["api"] = True
    except ImportError:
        deps["missing"].append("API: requests")

    return deps


def get_available_clients() -> list:
    """Get list of available client types"""
    deps = check_dependencies()
    available = []

    if deps["browser"]:
        available.append("browser")
    if deps["api"]:
        available.append("api")

    available.append("stub")  # Always available
    return available