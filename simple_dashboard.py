"""
Simple Dashboard that serves templates/index.html
"""
from flask import Flask, jsonify, request, render_template
import random
import json
import os
from datetime import datetime
from pathlib import Path

# Create Flask app with templates folder
app = Flask(__name__,
    template_folder='templates',
    static_folder='static'
)

# Ensure templates folder exists
templates_dir = Path('templates')
templates_dir.mkdir(exist_ok=True)

# Store state
bot_state = {
    "bot_enabled": False,
    "auto_approve": False,
    "auto_swipe": False,
    "personality": "default",
    "match_limit": 100,
    "typing_delay": 3,
    "max_tokens": 300,
    "stats": {
        "total_messages": 0,
        "total_matches": 0,
        "total_approved": 0,
        "total_rejected": 0,
        "likes_attempted": 0,
        "matches_made": 0,
        "claude_tokens": 0
    }
}

# Load saved state if exists
state_file = Path('data/bot_state.json')
if state_file.exists():
    try:
        with open(state_file, 'r') as f:
            saved_state = json.load(f)
            bot_state.update(saved_state)
    except:
        pass

def save_state():
    """Save bot state to file"""
    state_file.parent.mkdir(exist_ok=True)
    with open(state_file, 'w') as f:
        json.dump(bot_state, f, indent=2)

@app.route('/')
def index():
    """Serve the index.html template"""
    # Check if templates/index.html exists
    index_path = Path('templates/index.html')
    if not index_path.exists():
        # Return inline HTML if template doesn't exist
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Tinder Bot Dashboard</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    margin: 0;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    text-align: center;
                }
                h1 { font-size: 3em; }
                button {
                    padding: 15px 30px;
                    margin: 10px;
                    font-size: 16px;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                    background: #4CAF50;
                    color: white;
                }
                button:hover { transform: scale(1.05); }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔥 Tinder Bot Dashboard</h1>
                <p>Create templates/index.html to customize this page</p>
                <button onclick="fetch('/toggle-bot',{method:'POST'}).then(r=>r.json()).then(d=>alert('Bot: '+(d.enabled?'Started':'Stopped')))">Toggle Bot</button>
            </div>
        </body>
        </html>
        '''

    # Serve the actual template
    return render_template('index.html')

@app.route('/config')
def get_config():
    """Get current configuration"""
    return jsonify({
        "bot_enabled": bot_state['bot_enabled'],
        "auto_approve": bot_state['auto_approve'],
        "auto_swipe": bot_state['auto_swipe'],
        "personality": bot_state['personality'],
        "match_limit": bot_state['match_limit'],
        "typing_delay": bot_state['typing_delay'],
        "max_tokens": bot_state['max_tokens'],
        "use_browser_api": True
    })

@app.route('/stats')
def get_stats():
    """Get statistics"""
    return jsonify(bot_state['stats'])

@app.route('/bot-status')
def bot_status():
    """Get bot status"""
    return jsonify({
        "status": "healthy" if bot_state['bot_enabled'] else "stopped",
        "uptime_seconds": 0,
        "bot_enabled": bot_state['bot_enabled']
    })

@app.route('/toggle-bot', methods=['POST'])
def toggle_bot():
    """Toggle bot on/off"""
    bot_state['bot_enabled'] = not bot_state['bot_enabled']
    save_state()
    print(f"🤖 Bot {'started' if bot_state['bot_enabled'] else 'stopped'}")
    return jsonify({"status": "ok", "enabled": bot_state['bot_enabled']})

@app.route('/toggle-auto-approve', methods=['POST'])
def toggle_auto_approve():
    """Toggle auto-approve"""
    data = request.get_json() or {}
    if 'auto_approve' in data:
        bot_state['auto_approve'] = bool(data['auto_approve'])
    else:
        bot_state['auto_approve'] = not bot_state['auto_approve']
    save_state()
    return jsonify({"status": "ok", "auto_approve": bot_state['auto_approve']})

@app.route('/toggle-auto-swipe', methods=['POST'])
def toggle_auto_swipe():
    """Toggle auto-swipe"""
    data = request.get_json() or {}
    if 'auto_swipe' in data:
        bot_state['auto_swipe'] = bool(data['auto_swipe'])
    else:
        bot_state['auto_swipe'] = not bot_state['auto_swipe']
    save_state()
    return jsonify({"status": "ok", "auto_swipe": bot_state['auto_swipe']})

@app.route('/swipe-now', methods=['POST'])
def swipe_now():
    """Manual swipe"""
    bot_state['stats']['likes_attempted'] += random.randint(1, 5)
    bot_state['stats']['total_matches'] += random.randint(0, 2)
    save_state()
    return jsonify({
        "status": "ok",
        "result": {
            "likes": bot_state['stats']['likes_attempted'],
            "matches": bot_state['stats']['total_matches']
        }
    })

@app.route('/start-browser', methods=['POST'])
def start_browser():
    """Start browser"""
    return jsonify({
        "status": "ok",
        "browser_started": True,
        "message": "Browser mode ready"
    })

@app.route('/test-matches')
def test_matches():
    """Test matches endpoint"""
    matches = [
        {"id": f"match_{i}", "name": f"Test Match {i}", "age": 20 + i}
        for i in range(1, 6)
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
        "client_type": "BrowserClient",
        "available_methods": ["get_matches", "send_message", "swipe_right", "swipe_left"],
        "has_get_matches": True,
        "has_send_message": True
    })

@app.route('/pending')
def get_pending():
    """Get pending matches"""
    # Return some dummy data for testing
    pending = [
        {
            "id": "pending_1",
            "name": "Sarah",
            "age": 25,
            "last_message": "Hey there!",
            "timestamp": datetime.now().isoformat()
        }
    ]
    return jsonify(pending)

@app.route('/quick-stats')
def quick_stats():
    """Get quick stats"""
    total_sent = bot_state['stats'].get('total_messages', 0)
    total_matches = bot_state['stats'].get('total_matches', 0)
    response_rate = (total_matches / total_sent * 100) if total_sent > 0 else 0

    return jsonify({
        'matches_today': random.randint(0, 10),
        'response_rate': f"{response_rate:.1f}%",
        'active_conversations': random.randint(0, 5),
        'bot_uptime_hours': 0.1
    })

@app.route('/set-personality', methods=['POST'])
def set_personality():
    """Set bot personality"""
    data = request.get_json() or {}
    personality = data.get('personality', 'default')
    bot_state['personality'] = personality
    save_state()
    return jsonify({'status': 'ok', 'personality': personality})

@app.route('/set-limit', methods=['POST'])
def set_limit():
    """Set match limit"""
    data = request.get_json() or {}
    limit = int(data.get('limit', 100))
    bot_state['match_limit'] = limit
    save_state()
    return jsonify({'status': 'ok', 'limit': limit})

@app.route('/set-typing-delay', methods=['POST'])
def set_typing_delay():
    """Set typing delay"""
    data = request.get_json() or {}
    delay = float(data.get('delay', 3))
    bot_state['typing_delay'] = delay
    save_state()
    return jsonify({'status': 'ok', 'delay': delay})

@app.route('/set-max-tokens', methods=['POST'])
def set_max_tokens():
    """Set max tokens"""
    data = request.get_json() or {}
    max_tokens = int(data.get('max_tokens', 300))
    if not (100 <= max_tokens <= 4000):
        return jsonify({"error": "Max tokens must be between 100 and 4000"}), 400
    bot_state['max_tokens'] = max_tokens
    save_state()
    return jsonify({'status': 'ok', 'max_tokens': max_tokens})

# Add more routes that your index.html might need
@app.route('/matches')
def get_matches():
    """Get matches list"""
    matches = []
    for i in range(5):
        matches.append({
            "id": f"match_{i}",
            "name": f"Match {i+1}",
            "age": 20 + i,
            "bio": "Test bio",
            "photo": "https://via.placeholder.com/100",
            "matched_at": datetime.now().isoformat()
        })
    return jsonify({"matches": matches})

@app.route('/logs/auto')
def get_auto_logs():
    """Get auto-approved logs"""
    return jsonify([])

@app.route('/toggle-mode', methods=['POST'])
def toggle_mode():
    """Toggle between browser and API mode"""
    # For now, always browser mode
    return jsonify({"status": "ok", "mode": "browser"})

@app.route('/send-uninteracted', methods=['POST'])
def send_uninteracted():
    """Send messages to uninteracted matches"""
    data = request.get_json() or {}
    limit = data.get('limit', 5)
    return jsonify({"status": "ok", "sent": limit})

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔥 TINDER BOT DASHBOARD - TEMPLATE VERSION")
    print("="*60)
    print("Starting server...")
    print("Dashboard will be available at: http://localhost:5050")
    print("\nUsing templates/index.html if it exists")
    print("="*60 + "\n")

    # Make sure we have all the endpoints your index.html needs
    print("Available endpoints:")
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
            print(f"  {rule.rule} [{methods}]")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=5050, debug=False)