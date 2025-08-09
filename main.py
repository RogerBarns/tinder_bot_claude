"""
Main entry point for Tinder Bot
"""
import os
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import config, TINDER_AUTH_TOKEN, CLAUDE_API_KEY
from web.app import start_web_app
from utils.logger import setup_logging

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)


def check_environment():
    """Verify required environment variables"""
    missing = []

    if not TINDER_AUTH_TOKEN:
        missing.append("TINDER_AUTH_TOKEN")

    if not CLAUDE_API_KEY:
        missing.append("CLAUDE_API_KEY")

    if missing:
        logger.error(f"❌ Missing required environment variables: {', '.join(missing)}")
        logger.error("Please check your .env file")
        return False

    logger.info("✅ Environment check passed")
    return True


def verify_claude_api():
    """Test Claude API connection"""
    from personality.generator import MessageGenerator

    try:
        generator = MessageGenerator()
        test_reply = generator.generate_reply(
            name="Test",
            bio="Test bio",
            chat_history=[],
            personality="default"
        )

        if test_reply:
            logger.info("✅ Claude API verified")
            return True
        else:
            logger.error("❌ Claude API test failed")
            return False

    except Exception as e:
        logger.error(f"❌ Claude API error: {e}")
        return False


def main():
    """Main application entry point"""
    logger.info("🚀 Starting Tinder Bot...")

    # Environment check
    if not check_environment():
        sys.exit(1)

    # Verify Claude API
    if not verify_claude_api():
        logger.warning("⚠️ Claude API not working, bot may fail to generate messages")

    # Load saved configuration
    logger.info(f"📋 Configuration loaded: {dict(list(config.all.items())[:5])}...")  # Show first 5 items

    # Set initial states
    config.set("bot_enabled", True)
    config.set("auto_swipe", True)

    logger.info("🌐 Starting web dashboard...")

    try:
        # Start web app
        start_web_app(host="0.0.0.0", port=5555)
    except KeyboardInterrupt:
        logger.info("👋 Shutting down...")
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        raise


if __name__ == "__main__":
    # Only run if not in Flask reloader
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not os.environ.get("WERKZEUG_RUN_MAIN"):
        main()
