"""
Flask web application and API endpoints
"""
import os
import json
import threading
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, render_template, jsonify, request, send_file
from flask_socketio import SocketIO
from apscheduler.schedulers.background import BackgroundScheduler

from config import config, DATA_DIR
from core.api_client import TinderAPIClient
from core.message_handler import MessageHandler
from core.swipe_handler import SwipeHandler
from utils.logger import get_logger
from utils.stats import StatsManager

logger = get_logger(__name__)

# Initialize Flask app
app = Flask(__name__, 
    template_folder=Path(__file__).parent.parent / "templates",
    static_folder=Path(__file__).parent.parent / "static"
)
app.config['SECRET_KEY'] = os.urandom(24)

# Initialize SocketIO
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*")

# Initialize components
api_client = TinderAPIClient()
message_handler = MessageHandler()
swipe_handler = SwipeHandler()
stats_manager = StatsManager()

# Bot state
bot_start_time = datetime.now(timezone.utc)
bot_thread = None
scheduler = BackgroundScheduler()

# Logs storage (in-memory for dashboard)
pending_logs = []
auto_approved_logs = []


def bot_loop():
    """Main bot loop"""
    logger.info("🤖 Bot loop started")
    
    while config.get("bot_enabled", False):
        try:
            # Process messages
            processed = message_handler.process_new_messages(socketio)
            
            # Add to logs for dashboard
            for log in processed:
                if log.get("auto"):
                    auto_approved_logs.append(log)
                else:
                    pending_logs.append(log)
            
            # Sleep with randomization
            import time
            import random
            sleep_time = random.uniform(30, 90)
            logger.info(f"💤 Sleeping for {sleep_time:.0f}s")
            time.sleep(sleep_time)
            
        except Exception as e:
            logger.error(f"Bot loop error: {e}")
            time.sleep(60)  # Error cooldown


# Routes
@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html', 
        logs=pending_logs, 
        bot_enabled=config.get("bot_enabled", False),
        test_mode=config.get("test_mode", False)
    )


@app.route('/toggle-bot', methods=['POST'])
def toggle_bot():
    """Start/stop the bot"""
    global bot_thread
    
    current_state = config.get("bot_enabled", False)
    new_state = not current_state
    config.set("bot_enabled", new_state)
    
    if new_state and (not bot_thread or not bot_thread.is_alive()):
        bot_thread = threading.Thread(target=bot_loop, daemon=True)
        bot_thread.start()
        logger.info("✅ Bot started")
    else:
        logger.info("🛑 Bot stopped")
    
    socketio.emit("bot_toggled", {"enabled": new_state})
    
    return jsonify({"status": "ok", "enabled": new_state})


@app.route('/toggle-auto-approve', methods=['POST'])
def toggle_auto_approve():
    """Toggle auto-approval mode"""
    state = request.json.get("auto_approve", False)
    config.set("auto_approve", state)
    
    logger.info(f"Auto-approve set to: {state}")
    return jsonify({"status": "ok", "auto_approve": state})


@app.route('/toggle-auto-swipe', methods=['POST'])
def toggle_auto_swipe():
    """Toggle auto-swipe feature"""
    state = request.json.get("auto_swipe", False)
    config.set("auto_swipe", state)
    
    # Update scheduler
    job_id = 'auto_swipe'
    if state:
        interval = config.get("swipe_interval", 30)
        if not scheduler.get_job(job_id):
            scheduler.add_job(
                swipe_handler.auto_swipe_and_message,
                'interval',
                minutes=interval,
                id=job_id
            )
        logger.info(f"Auto-swipe enabled (every {interval} min)")
    else:
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
        logger.info("Auto-swipe disabled")
    
    return jsonify({"status": "ok", "auto_swipe": state})


@app.route('/swipe-now', methods=['POST'])
def manual_swipe():
    """Trigger manual swipe"""
    try:
        result = swipe_handler.auto_swipe_and_message()
        return jsonify({"status": "ok", "result": result})
    except Exception as e:
        logger.error(f"Manual swipe error: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route('/message-uninteracted', methods=['POST'])
def message_uninteracted():
    """Send messages to unmatched profiles"""
    count = request.json.get("count", 5)
    
    try:
        result = message_handler.send_to_unmatched(count)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Message uninteracted error: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route('/approve/<match_id>', methods=['POST'])
def approve_match(match_id):
    """Approve a pending match"""
    global pending_logs
    
    # Find the match
    match_log = None
    for log in pending_logs:
        if log["match_id"] == match_id:
            match_log = log
            break
    
    if not match_log:
        return jsonify({"error": "Match not found"}), 404
    
    # Send the message
    if api_client.send_message(match_id, match_log["bot_reply"]):
        # Update stats
        stats_manager.increment("total_approved")
        stats_manager.increment("total_replied")
        
        # Remove from pending
        pending_logs = [l for l in pending_logs if l["match_id"] != match_id]
        
        # Add to auto-approved if in that mode
        if config.get("auto_approve"):
            match_log["auto"] = True
            auto_approved_logs.append(match_log)
        
        return jsonify({"status": "approved"})
    
    return jsonify({"error": "Failed to send message"}), 500


@app.route('/reject/<match_id>', methods=['POST'])
def reject_match(match_id):
    """Reject a pending match"""
    global pending_logs
    
    # Remove from pending
    pending_logs = [l for l in pending_logs if l["match_id"] != match_id]
    
    # Update stats
    stats_manager.increment("total_rejected")
    
    return jsonify({"status": "rejected"})


@app.route('/set-personality', methods=['POST'])
def set_personality():
    """Change bot personality"""
    personality = request.json.get('personality', 'default')
    config.set('personality', personality)
    
    return jsonify({'status': 'ok', 'personality': personality})


@app.route('/set-limit', methods=['POST'])
def set_match_limit():
    """Set match fetch limit"""
    limit = int(request.json.get('limit', 100))
    config.set('match_limit', limit)
    
    return jsonify({'status': 'ok', 'limit': limit})


@app.route('/set-swipe-interval', methods=['POST'])
def set_swipe_interval():
    """Set auto-swipe interval"""
    minutes = int(request.json.get('minutes', 30))
    config.set('swipe_interval', minutes)
    
    # Reschedule if active
    job_id = 'auto_swipe'
    if scheduler.get_job(job_id):
        scheduler.reschedule_job(job_id, trigger='interval', minutes=minutes)
    
    return jsonify({'status': 'ok', 'interval': minutes})


@app.route('/set-typing-delay', methods=['POST'])
def set_typing_delay():
    """Set typing simulation delay"""
    delay = float(request.json.get('delay', 3))
    config.set('typing_delay', delay)
    
    return jsonify({'status': 'ok', 'delay': delay})


@app.route('/set-max-tokens', methods=['POST'])
def set_max_tokens():
    """Set Claude max tokens"""
    max_tokens = int(request.json.get('max_tokens', 300))
    
    if not (100 <= max_tokens <= 4000):
        return jsonify({"error": "Max tokens must be between 100 and 4000"}), 400
    
    config.set('max_tokens', max_tokens)
    
    return jsonify({"status": "success", "max_tokens": max_tokens})


@app.route('/config')
def get_config():
    """Get current configuration"""
    return jsonify(config.all)


@app.route('/stats')
def get_stats():
    """Get bot statistics"""
    return jsonify(stats_manager.get_all())


@app.route('/bot-status')
def bot_status():
    """Get bot health status"""
    uptime = datetime.now(timezone.utc) - bot_start_time
    
    return jsonify({
        "status": "healthy" if config.get("bot_enabled") else "stopped",
        "uptime_seconds": int(uptime.total_seconds())
    })


@app.route('/pending')
def get_pending():
    """Get pending matches"""
    return jsonify(pending_logs)


@app.route('/logs/auto')
def get_auto_logs():
    """Get auto-approved logs"""
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 100))
    
    start = (page - 1) * limit
    end = start + limit
    
    # Sort newest first
    sorted_logs = sorted(
        auto_approved_logs, 
        key=lambda x: x.get("timestamp", ""),
        reverse=True
    )
    
    return jsonify(sorted_logs[start:end])


@app.route('/claude-usage')
def claude_usage():
    """Get Claude API usage stats"""
    usage_file = DATA_DIR / "claude_usage.json"
    
    if usage_file.exists():
        with open(usage_file, 'r') as f:
            usage = json.load(f)
    else:
        usage = {"total_tokens": 0, "by_model": {}}
    
    return jsonify({
        "claude_tokens": usage.get("total_tokens", 0),
        "per_model_tokens": usage.get("by_model", {})
    })


@app.route('/download-logs')
def download_logs():
    """Download chat logs"""
    return send_file(DATA_DIR / "chat_log.json", as_attachment=True)


@app.route('/download-history')  
def download_history():
    """Download full conversation history"""
    return send_file(DATA_DIR / "full_history.json", as_attachment=True)


# Socket.IO events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info("✅ Client connected to WebSocket")


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info("❌ Client disconnected from WebSocket")


def start_web_app(host="0.0.0.0", port=5000):
    """Start the web application"""
    # Start scheduler
    scheduler.start()
    
    # Run Flask app
    socketio.run(app, host=host, port=port, use_reloader=False)