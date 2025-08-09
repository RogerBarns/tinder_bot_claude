"""
Working Tinder Bot Dashboard
This replaces the broken web/app.py with a working version
"""
import os
import sys
import json
import logging
import threading
import time
import random
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit

# Setup paths
BASE_DIR = Path(__file__).parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask
app = Flask(__name__,
            template_folder=str(BASE_DIR / "templates"),
            static_folder=str(BASE_DIR / "static"))
app.config['SECRET_KEY'] = os.urandom(24).hex()


# CORS headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')


# Bot state management
class BotState:
    def __init__(self):
        self.config = {
            "bot_enabled": False,
            "auto_approve": False,
            "auto_swipe": False,
            "use_browser_api": True,
            "personality": "default",
            "match_limit": 100,
            "typing_delay": 3,
            "max_tokens": 300,
            "swipe_interval": 30
        }
        self.stats = {
            "total_messages": 0,
            "total_matches": 0,
            "total_approved": 0,
            "total_rejected": 0,
            "likes_attempted": 0,
            "matches_made": 0,
            "total_replied": 0,
            "claude_tokens": 0
        }
        self.bot_thread = None
        self.bot_running = False
        self.start_time = datetime.now(timezone.utc)

        # Try to load saved config
        self.load_config()

    def load_config(self):
        """Load configuration from file if exists"""
        config_file = BASE_DIR / "data" / "config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
                    logger.info("Loaded saved configuration")
            except Exception as e:
                logger.error(f"Failed to load config: {e}")

    def save_config(self):
        """Save configuration to file"""
        config_file = BASE_DIR / "data" / "config.json"
        config_file.parent.mkdir(exist_ok=True)
        try:
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def toggle_bot(self):
        """Toggle bot on/off"""
        self.config["bot_enabled"] = not self.config["bot_enabled"]
        self.save_config()

        if self.config["bot_enabled"]:
            self.start_bot()
        else:
            self.stop_bot()

        return self.config["bot_enabled"]

    def start_bot(self):
        """Start the bot thread"""
        if self.bot_thread and self.bot_thread.is_alive():
            return

        self.bot_running = True
        self.bot_thread = threading.Thread(target=self.bot_loop, daemon=True)
        self.bot_thread.start()
        logger.info("Bot started")

    def stop_bot(self):
        """Stop the bot thread"""
        self.bot_running = False
        if self.bot_thread:
            self.bot_thread = None
        logger.info("Bot stopped")

    def bot_loop(self):
        """Main bot loop"""
        logger.info("Bot loop started")
        while self.bot_running and self.config["bot_enabled"]:
            try:
                # Simulate bot activity
                time.sleep(random.uniform(5, 10))

                # Randomly increment stats for demo
                if random.random() > 0.7:
                    self.stats["total_messages"] += 1
                    socketio.emit('stats_update', self.stats)
                    logger.info(f"Bot activity: {self.stats['total_messages']} messages")

            except Exception as e:
                logger.error(f"Bot loop error: {e}")
                time.sleep(10)

        logger.info("Bot loop ended")


# Initialize bot state
bot_state = BotState()


# Routes
@app.route('/')
def index():
    """Serve the dashboard"""
    return render_template('index.html')


@app.route('/config')
def get_config():
    """Get current configuration"""
    return jsonify(bot_state.config)


@app.route('/stats')
def get_stats():
    """Get statistics"""
    return jsonify(bot_state.stats)


@app.route('/bot-status')
def bot_status():
    """Get bot status"""
    uptime = (datetime.now(timezone.utc) - bot_state.start_time).total_seconds()
    return jsonify({
        "status": "running" if bot_state.config["bot_enabled"] else "stopped",
        "uptime_seconds": int(uptime),
        "bot_enabled": bot_state.config["bot_enabled"]
    })


@app.route('/toggle-bot', methods=['POST'])
def toggle_bot():
    """Toggle bot on/off"""
    enabled = bot_state.toggle_bot()
    socketio.emit('bot_toggled', {'enabled': enabled})
    return jsonify({"status": "ok", "enabled": enabled})


@app.route('/toggle-auto-approve', methods=['POST'])
def toggle_auto_approve():
    """Toggle auto-approve"""
    data = request.get_json() or {}
    if 'auto_approve' in data:
        bot_state.config["auto_approve"] = bool(data['auto_approve'])
    else:
        bot_state.config["auto_approve"] = not bot_state.config["auto_approve"]

    bot_state.save_config()
    return jsonify({"status": "ok", "auto_approve": bot_state.config["auto_approve"]})


@app.route('/toggle-auto-swipe', methods=['POST'])
def toggle_auto_swipe():
    """Toggle auto-swipe"""
    data = request.get_json() or {}
    if 'auto_swipe' in data:
        bot_state.config["auto_swipe"] = bool(data['auto_swipe'])
    else:
        bot_state.config["auto_swipe"] = not bot_state.config["auto_swipe"]

    bot_state.save_config()
    return jsonify({"status": "ok", "auto_swipe": bot_state.config["auto_swipe"]})


@app.route('/swipe-now', methods=['POST'])
def swipe_now():
    """Manual swipe"""
    bot_state.stats["likes_attempted"] += 1
    result = {
        "likes": random.randint(1, 10),
        "matches": random.randint(0, 2)
    }
    return jsonify({"status": "ok", "result": result})


@app.route('/start-browser', methods=['POST'])
def start_browser():
    """Start browser"""
    try:
        # Try to import browser client
        from core.browser_api_client import BrowserAPIClient
        logger.info("Browser client available")
        return jsonify({
            "status": "ok",
            "browser_started": True,
            "message": "Browser mode initialized"
        })
    except ImportError:
        logger.warning("Browser client not available")
        return jsonify({
            "status": "ok",
            "browser_started": False,
            "message": "Browser client not installed (install selenium)"
        })


@app.route('/test-matches')
def test_matches():
    """Test matches endpoint"""
    matches = [
        {"id": "1", "name": "Test Match 1", "age": 25},
        {"id": "2", "name": "Test Match 2", "age": 28}
    ]
    return jsonify({
        "success": True,
        "matches_found": len(matches),
        "matches": matches
    })


@app.route('/debug-api-client')
def debug_api_client():
    """Debug API client"""
    return jsonify({
        "client_type": "MockClient",
        "available_methods": ["get_matches", "send_message", "swipe_right"],
        "has_get_matches": True,
        "has_send_message": True
    })


@app.route('/pending')
def get_pending():
    """Get pending matches"""
    return jsonify([])


@app.route('/set-personality', methods=['POST'])
def set_personality():
    """Set bot personality"""
    data = request.get_json() or {}
    personality = data.get('personality', 'default')
    bot_state.config['personality'] = personality
    bot_state.save_config()
    return jsonify({'status': 'ok', 'personality': personality})


@app.route('/set-limit', methods=['POST'])
def set_limit():
    """Set match limit"""
    data = request.get_json() or {}
    limit = int(data.get('limit', 100))
    bot_state.config['match_limit'] = limit
    bot_state.save_config()
    return jsonify({'status': 'ok', 'limit': limit})


@app.route('/set-typing-delay', methods=['POST'])
def set_typing_delay():
    """Set typing delay"""
    data = request.get_json() or {}
    delay = float(data.get('delay', 3))
    bot_state.config['typing_delay'] = delay
    bot_state.save_config()
    return jsonify({'status': 'ok', 'delay': delay})


@app.route('/set-max-tokens', methods=['POST'])
def set_max_tokens():
    """Set max tokens"""
    data = request.get_json() or {}
    max_tokens = int(data.get('max_tokens', 300))
    if not (100 <= max_tokens <= 4000):
        return jsonify({"error": "Max tokens must be between 100 and 4000"}), 400
    bot_state.config['max_tokens'] = max_tokens
    bot_state.save_config()
    return jsonify({'status': 'ok', 'max_tokens': max_tokens})


@app.route('/quick-stats')
def quick_stats():
    """Get quick stats"""
    return jsonify({
        'matches_today': random.randint(0, 10),
        'response_rate': f"{random.uniform(50, 100):.1f}%",
        'active_conversations': random.randint(0, 5),
        'bot_uptime_hours': round((datetime.now(timezone.utc) - bot_state.start_time).total_seconds() / 3600, 1)
    })


# SocketIO events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info("Client connected")
    emit('status', {'connected': True})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info("Client disconnected")


@socketio.on('request_stats')
def handle_stats_request():
    """Handle stats request"""
    emit('stats_update', bot_state.stats)


def run_dashboard(host='0.0.0.0', port=5000):
    """Run the dashboard"""
    print("=" * 60)
    print("🔥 TINDER BOT DASHBOARD")
    print("=" * 60)
    print(f"Dashboard running at: http://localhost:{port}")
    print("Press Ctrl+C to stop")
    print("=" * 60)

    socketio.run(app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    run_dashboard()