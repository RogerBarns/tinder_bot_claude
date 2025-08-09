"""
Dashboard with real browser integration for Tinder (No SocketIO)
Works with Python 3.13
"""
from flask import Flask, jsonify, request, render_template
import os
import json
import random
import threading
import time
from pathlib import Path
from datetime import datetime

# Try to import Selenium
try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.keys import Keys
    SELENIUM_AVAILABLE = True
    print("✅ Selenium and undetected-chromedriver available")
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️ Selenium not available. Install with: pip install undetected-chromedriver selenium")

# Get the absolute path to templates
BASE_DIR = Path(__file__).parent.absolute()
TEMPLATES_DIR = BASE_DIR / "templates"

# Create Flask app
app = Flask(__name__,
    template_folder=str(TEMPLATES_DIR)
)

# Global browser instance
browser_driver = None
browser_thread = None
auto_swipe_thread = None

# Bot state
bot_state = {
    "bot_enabled": False,
    "auto_approve": False,
    "auto_swipe": False,
    "personality": "default",
    "browser_running": False,
    "stats": {
        "total_messages": 0,
        "total_matches": 0,
        "total_approved": 0,
        "total_rejected": 0,
        "likes_attempted": 0,
        "claude_tokens": 0
    },
    "logs": []
}

class TinderBrowser:
    """Handle Tinder browser automation"""

    def __init__(self):
        self.driver = None
        self.is_logged_in = False

    def start_browser(self):
        """Start the Chrome browser"""
        if not SELENIUM_AVAILABLE:
            return False, "Selenium not installed. Run: pip install undetected-chromedriver selenium"

        try:
            print("🌐 Starting Chrome browser...")
            bot_state['logs'].append({"time": datetime.now().isoformat(), "message": "Starting Chrome browser..."})

            # Chrome options
            options = uc.ChromeOptions()

            # Create profile directory for persistent login
            profile_dir = BASE_DIR / "data" / "chrome_profile"
            profile_dir.mkdir(parents=True, exist_ok=True)
            options.add_argument(f'--user-data-dir={str(profile_dir)}')

            # Other options
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--window-size=1366,768')

            # Start Chrome
            print("Initializing Chrome driver...")
            self.driver = uc.Chrome(options=options, version_main=None)

            print("✅ Chrome browser started")
            bot_state['logs'].append({"time": datetime.now().isoformat(), "message": "Chrome browser started successfully"})

            # Navigate to Tinder
            print("📍 Navigating to Tinder...")
            self.driver.get("https://tinder.com")

            # Wait a bit for page to load
            time.sleep(3)

            # Check if already logged in
            if self.check_logged_in():
                print("✅ Already logged in to Tinder")
                self.is_logged_in = True
                bot_state['browser_running'] = True
                return True, "Browser started and logged in! You can now use swipe features."
            else:
                print("⚠️ Not logged in - please complete login manually in the Chrome window")
                bot_state['browser_running'] = True
                return True, "Browser started! Please login to Tinder in the Chrome window, then you can use the bot features."

        except Exception as e:
            print(f"❌ Error starting browser: {e}")
            bot_state['logs'].append({"time": datetime.now().isoformat(), "message": f"Error: {str(e)}"})
            return False, f"Error starting browser: {str(e)}"

    def check_logged_in(self):
        """Check if logged into Tinder"""
        try:
            # Check for elements that appear when logged in
            logged_in_indicators = [
                "[data-testid='gamepad']",
                ".recsCardboard",
                "[href='/app/recs']",
                ".gamepad",
                "[aria-label='Like']",
                "[aria-label='Nope']"
            ]

            for selector in logged_in_indicators:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    return True

            # Check URL
            current_url = self.driver.current_url
            if any(path in current_url for path in ["/app/recs", "/app/likes", "/app/matches"]):
                return True

            return False
        except:
            return False

    def swipe_right(self):
        """Swipe right (like)"""
        if not self.driver:
            return False, "Browser not started"

        if not self.is_logged_in:
            # Check again if we're logged in now
            self.is_logged_in = self.check_logged_in()
            if not self.is_logged_in:
                return False, "Not logged in to Tinder"

        try:
            # Navigate to discovery if not there
            if "/app/recs" not in self.driver.current_url:
                self.driver.get("https://tinder.com/app/recs")
                time.sleep(2)

            # Try multiple methods to swipe
            # Method 1: Click Like button
            try:
                like_button = self.driver.find_element(By.CSS_SELECTOR, "[aria-label='Like']")
                like_button.click()
                return True, "Swiped right!"
            except:
                pass

            # Method 2: Keyboard shortcut
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.ARROW_RIGHT)
                return True, "Swiped right!"
            except:
                pass

            # Method 3: Alternative selectors
            try:
                like_selectors = [
                    "button[type='button']:has(span:contains('LIKE'))",
                    ".gamepad-button--like",
                    "[data-testid='gamepad-like']"
                ]
                for selector in like_selectors:
                    try:
                        button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        button.click()
                        return True, "Swiped right!"
                    except:
                        continue
            except:
                pass

            return False, "Could not find swipe button"

        except Exception as e:
            return False, f"Error swiping: {str(e)}"

    def close_browser(self):
        """Close the browser"""
        if self.driver:
            try:
                self.driver.quit()
                print("🧹 Browser closed")
                bot_state['browser_running'] = False
            except:
                pass
            self.driver = None
            self.is_logged_in = False

# Initialize browser manager
tinder_browser = TinderBrowser()

try:
    from message_handler import MessageHandler
    from claude_handler import ClaudeHandler
    MESSAGE_HANDLER_AVAILABLE = True
    print("✅ Message handler loaded")
except ImportError:
    MESSAGE_HANDLER_AVAILABLE = False
    print("⚠️ Message handler not available")

# Initialize message handler (add after tinder_browser initialization)
if MESSAGE_HANDLER_AVAILABLE and tinder_browser.driver:
    claude = ClaudeHandler()
    message_handler = MessageHandler(tinder_browser.driver, claude)
else:
    message_handler = None

# Add this route to your dashboard_browser.py

@app.route('/process-messages', methods=['POST'])
def process_messages():
    """Process and reply to messages"""
    if not tinder_browser.driver:
        return jsonify({
            "status": "error",
            "message": "Browser not started"
        })

    if not tinder_browser.is_logged_in:
        return jsonify({
            "status": "error",
            "message": "Not logged in to Tinder"
        })

    if not message_handler:
        return jsonify({
            "status": "error",
            "message": "Message handler not initialized"
        })

    # Process messages
    replied_count = message_handler.process_new_messages()

    return jsonify({
        "status": "ok",
        "replied_to": replied_count,
        "message": f"Replied to {replied_count} matches"
    })

# Add auto-reply functionality (add to toggle_bot route)
# When bot is enabled, start auto-reply thread
def auto_reply_loop():
    """Auto-reply to messages"""
    while bot_state['bot_enabled']:
        if tinder_browser.driver and tinder_browser.is_logged_in and message_handler:
            replied = message_handler.process_new_messages()
            if replied > 0:
                print(f"📬 Auto-replied to {replied} matches")
        time.sleep(60)  # Check every minute

# Start auto-reply thread when bot is enabled
if bot_state['bot_enabled']:
    reply_thread = threading.Thread(target=auto_reply_loop, daemon=True)
    reply_thread.start()


@app.route('/')
def index():
    """Serve the dashboard"""
    return render_template('index.html')

@app.route('/config')
def get_config():
    return jsonify({
        "bot_enabled": bot_state['bot_enabled'],
        "auto_approve": bot_state['auto_approve'],
        "auto_swipe": bot_state['auto_swipe'],
        "personality": bot_state.get('personality', 'default'),
        "match_limit": 100,
        "typing_delay": 4,
        "max_tokens": 300,
        "use_browser_api": True
    })

@app.route('/stats')
def get_stats():
    return jsonify(bot_state['stats'])

@app.route('/bot-status')
def bot_status():
    return jsonify({
        "status": "healthy" if bot_state['bot_enabled'] else "stopped",
        "uptime_seconds": 0,
        "bot_enabled": bot_state['bot_enabled'],
        "browser_running": bot_state['browser_running'],
        "logged_in": tinder_browser.is_logged_in
    })

@app.route('/toggle-bot', methods=['POST'])
def toggle_bot():
    bot_state['bot_enabled'] = not bot_state['bot_enabled']

    if bot_state['bot_enabled']:
        print("🤖 Bot started")
        bot_state['logs'].append({"time": datetime.now().isoformat(), "message": "Bot started"})
    else:
        print("🛑 Bot stopped")
        bot_state['logs'].append({"time": datetime.now().isoformat(), "message": "Bot stopped"})

    return jsonify({"status": "ok", "enabled": bot_state['bot_enabled']})

@app.route('/toggle-auto-approve', methods=['POST'])
def toggle_auto_approve():
    bot_state['auto_approve'] = not bot_state['auto_approve']
    return jsonify({"status": "ok", "auto_approve": bot_state['auto_approve']})

@app.route('/toggle-auto-swipe', methods=['POST'])
def toggle_auto_swipe():
    global auto_swipe_thread
    bot_state['auto_swipe'] = not bot_state['auto_swipe']

    if bot_state['auto_swipe']:
        # Start auto-swipe thread
        def auto_swipe_loop():
            print("🔄 Auto-swipe thread started")
            while bot_state['auto_swipe']:
                if tinder_browser.driver and tinder_browser.is_logged_in:
                    success, message = tinder_browser.swipe_right()
                    if success:
                        bot_state['stats']['likes_attempted'] += 1
                        print(f"👍 Auto-swipe: {message}")
                        bot_state['logs'].append({"time": datetime.now().isoformat(), "message": f"Auto-swipe: {message}"})
                    else:
                        print(f"⚠️ Auto-swipe failed: {message}")

                    # Wait between swipes (2-5 seconds)
                    time.sleep(random.uniform(2, 5))
                else:
                    # Wait and check again
                    time.sleep(5)
            print("🔄 Auto-swipe thread stopped")

        auto_swipe_thread = threading.Thread(target=auto_swipe_loop, daemon=True)
        auto_swipe_thread.start()
        print("🔄 Auto-swipe enabled")
        bot_state['logs'].append({"time": datetime.now().isoformat(), "message": "Auto-swipe enabled"})
    else:
        print("⏸️ Auto-swipe disabled")
        bot_state['logs'].append({"time": datetime.now().isoformat(), "message": "Auto-swipe disabled"})

    return jsonify({"status": "ok", "auto_swipe": bot_state['auto_swipe']})

@app.route('/start-browser', methods=['POST'])
def start_browser():
    """Start the actual browser"""
    print("🚀 Start browser request received")

    if tinder_browser.driver:
        return jsonify({
            "status": "ok",
            "browser_started": True,
            "message": "Browser already running"
        })

    # Start browser
    success, message = tinder_browser.start_browser()

    return jsonify({
        "status": "ok" if success else "error",
        "browser_started": success,
        "message": message
    })

@app.route('/stop-browser', methods=['POST'])
def stop_browser():
    """Stop the browser"""
    tinder_browser.close_browser()
    bot_state['browser_running'] = False
    return jsonify({
        "status": "ok",
        "browser_stopped": True,
        "message": "Browser closed"
    })

@app.route('/swipe-now', methods=['POST'])
def swipe_now():
    """Manual swipe"""
    if tinder_browser.driver:
        success, message = tinder_browser.swipe_right()
        if success:
            bot_state['stats']['likes_attempted'] += 1
            bot_state['logs'].append({"time": datetime.now().isoformat(), "message": message})
        return jsonify({
            "status": "ok" if success else "error",
            "result": {"likes": 1 if success else 0, "matches": 0},
            "message": message
        })
    else:
        return jsonify({
            "status": "error",
            "result": {"likes": 0, "matches": 0},
            "message": "Browser not started. Click 'Start Browser' first."
        })

@app.route('/logs')
def get_logs():
    """Get recent activity logs"""
    # Return last 20 logs
    return jsonify(bot_state['logs'][-20:])

@app.route('/test-matches')
def test_matches():
    return jsonify({
        "success": True,
        "matches_found": 2,
        "matches": [
            {"id": "1", "name": "Test Match 1", "age": 25},
            {"id": "2", "name": "Test Match 2", "age": 28}
        ]
    })

@app.route('/debug-api-client')
def debug_api_client():
    return jsonify({
        "client_type": "BrowserClient",
        "selenium_available": SELENIUM_AVAILABLE,
        "browser_running": tinder_browser.driver is not None,
        "logged_in": tinder_browser.is_logged_in,
        "available_methods": ["get_matches", "send_message", "swipe_right", "swipe_left"]
    })

@app.route('/pending')
def get_pending():
    return jsonify([])

@app.route('/quick-stats')
def quick_stats():
    return jsonify({
        'matches_today': 0,
        'response_rate': "0%",
        'active_conversations': 0,
        'bot_uptime_hours': 0
    })

# Add all other endpoints
@app.route('/set-personality', methods=['POST'])
def set_personality():
    data = request.get_json() or {}
    bot_state['personality'] = data.get('personality', 'default')
    return jsonify({'status': 'ok', 'personality': bot_state['personality']})

@app.route('/set-limit', methods=['POST'])
def set_limit():
    return jsonify({'status': 'ok', 'limit': 100})

@app.route('/set-typing-delay', methods=['POST'])
def set_typing_delay():
    return jsonify({'status': 'ok', 'delay': 4})

@app.route('/set-max-tokens', methods=['POST'])
def set_max_tokens():
    return jsonify({'status': 'ok', 'max_tokens': 300})

@app.route('/matches')
def get_matches():
    return jsonify({"matches": []})

@app.route('/toggle-mode', methods=['POST'])
def toggle_mode():
    return jsonify({"status": "ok", "mode": "browser"})

@app.route('/send-uninteracted', methods=['POST'])
def send_uninteracted():
    return jsonify({"status": "ok", "sent": 0})

# Clean shutdown
import atexit
def cleanup():
    if tinder_browser.driver:
        tinder_browser.close_browser()

atexit.register(cleanup)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔥 TINDER BOT DASHBOARD WITH BROWSER INTEGRATION")
    print("="*60)

    if SELENIUM_AVAILABLE:
        print("✅ Selenium is installed - browser automation ready")
        print("\nHow to use:")
        print("1. Click 'Start Browser' to open Chrome")
        print("2. Login to Tinder manually (first time only)")
        print("3. Use 'Swipe Now' or enable 'Auto-Swipe'")
        print("4. Your login will be saved for next time")
    else:
        print("⚠️ Selenium not installed - browser features disabled")
        print("   Install with: pip install undetected-chromedriver selenium")

    print(f"\nTemplates directory: {TEMPLATES_DIR}")
    print(f"Templates exist: {TEMPLATES_DIR.exists()}")

    print("\nDashboard at: http://localhost:5050")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=5050, debug=False)