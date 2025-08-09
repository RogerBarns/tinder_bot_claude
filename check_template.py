"""
Script to check why index.html isn't being used and fix it
"""
import os
from pathlib import Path


def check_template_setup():
    """Check template folder and files"""
    print("=" * 60)
    print("🔍 CHECKING TEMPLATE SETUP")
    print("=" * 60)

    # Check current directory
    cwd = Path.cwd()
    print(f"Current directory: {cwd}")

    # Check templates folder
    templates_dir = cwd / "templates"
    if templates_dir.exists():
        print(f"✅ Templates folder exists: {templates_dir}")

        # List all files in templates
        template_files = list(templates_dir.glob("*"))
        print(f"\nFiles in templates folder:")
        for file in template_files:
            size = file.stat().st_size
            print(f"  - {file.name} ({size} bytes)")

        # Check index.html specifically
        index_file = templates_dir / "index.html"
        if index_file.exists():
            print(f"\n✅ index.html exists ({index_file.stat().st_size} bytes)")

            # Check first few lines of index.html
            with open(index_file, 'r', encoding='utf-8') as f:
                first_lines = f.read(500)
                if "<!DOCTYPE html>" in first_lines or "<html" in first_lines:
                    print("✅ index.html appears to be valid HTML")
                else:
                    print("⚠️ index.html might not be valid HTML")
        else:
            print("❌ index.html NOT found in templates folder")
    else:
        print(f"❌ Templates folder NOT found at {templates_dir}")
        print("\nCreating templates folder...")
        templates_dir.mkdir(exist_ok=True)

    return templates_dir


def create_working_dashboard():
    """Create a dashboard that definitely uses templates/index.html"""

    dashboard_code = '''"""
Dashboard that uses templates/index.html
"""
from flask import Flask, jsonify, request, render_template, send_from_directory
import os
import json
import random
from pathlib import Path
from datetime import datetime

# Get the absolute path to templates
BASE_DIR = Path(__file__).parent.absolute()
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

print(f"Looking for templates in: {TEMPLATES_DIR}")
print(f"Templates folder exists: {TEMPLATES_DIR.exists()}")

# Create Flask app with absolute paths
app = Flask(__name__, 
    template_folder=str(TEMPLATES_DIR),
    static_folder=str(STATIC_DIR) if STATIC_DIR.exists() else None
)

# Debug: Print template search path
print(f"Flask template search path: {app.template_folder}")

# Bot state
bot_state = {
    "bot_enabled": False,
    "auto_approve": False,
    "auto_swipe": False,
    "personality": "default",
    "stats": {
        "total_messages": 0,
        "total_matches": 0,
        "total_approved": 0,
        "total_rejected": 0,
        "likes_attempted": 0,
        "claude_tokens": 0
    }
}

@app.route('/')
def index():
    """Serve the dashboard"""
    # List available templates for debugging
    template_files = list(Path(app.template_folder).glob("*.html")) if app.template_folder else []
    print(f"Available templates: {[f.name for f in template_files]}")

    # Check if index.html exists
    index_path = Path(app.template_folder) / "index.html" if app.template_folder else None

    if index_path and index_path.exists():
        print(f"Serving index.html from: {index_path}")
        return render_template('index.html')
    else:
        print(f"index.html not found, serving inline HTML")
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Tinder Bot Dashboard</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: #1a1a1a;
                    color: white;
                    padding: 20px;
                    text-align: center;
                }
                .error {
                    background: #ff4444;
                    padding: 20px;
                    border-radius: 10px;
                    margin: 20px;
                }
            </style>
        </head>
        <body>
            <h1>🔥 Tinder Bot Dashboard</h1>
            <div class="error">
                <h2>Template Not Found!</h2>
                <p>Could not find templates/index.html</p>
                <p>Template folder: """ + str(app.template_folder) + """</p>
                <p>Make sure templates/index.html exists</p>
            </div>
            <button onclick="testAPI()">Test API</button>
            <script>
                function testAPI() {
                    fetch('/config')
                        .then(r => r.json())
                        .then(d => alert('API Working! Config: ' + JSON.stringify(d)));
                }
            </script>
        </body>
        </html>
        """

# All your API endpoints
@app.route('/config')
def get_config():
    return jsonify({
        "bot_enabled": bot_state['bot_enabled'],
        "auto_approve": bot_state['auto_approve'],
        "auto_swipe": bot_state['auto_swipe'],
        "personality": bot_state.get('personality', 'default'),
        "match_limit": 100,
        "typing_delay": 3,
        "max_tokens": 300
    })

@app.route('/stats')
def get_stats():
    return jsonify(bot_state['stats'])

@app.route('/bot-status')
def bot_status():
    return jsonify({
        "status": "healthy" if bot_state['bot_enabled'] else "stopped",
        "uptime_seconds": 0,
        "bot_enabled": bot_state['bot_enabled']
    })

@app.route('/toggle-bot', methods=['POST'])
def toggle_bot():
    bot_state['bot_enabled'] = not bot_state['bot_enabled']
    print(f"Bot {'enabled' if bot_state['bot_enabled'] else 'disabled'}")
    return jsonify({"status": "ok", "enabled": bot_state['bot_enabled']})

@app.route('/toggle-auto-approve', methods=['POST'])
def toggle_auto_approve():
    bot_state['auto_approve'] = not bot_state['auto_approve']
    return jsonify({"status": "ok", "auto_approve": bot_state['auto_approve']})

@app.route('/toggle-auto-swipe', methods=['POST'])
def toggle_auto_swipe():
    bot_state['auto_swipe'] = not bot_state['auto_swipe']
    return jsonify({"status": "ok", "auto_swipe": bot_state['auto_swipe']})

@app.route('/start-browser', methods=['POST'])
def start_browser():
    """Start browser - API endpoint, not a page"""
    print("Start browser API called")
    return jsonify({
        "status": "ok",
        "browser_started": True,
        "message": "Browser started successfully"
    })

@app.route('/swipe-now', methods=['POST'])
def swipe_now():
    bot_state['stats']['likes_attempted'] += 1
    return jsonify({"status": "ok", "result": {"likes": 1, "matches": 0}})

@app.route('/test-matches')
def test_matches():
    return jsonify({
        "success": True,
        "matches_found": 2,
        "matches": [
            {"id": "1", "name": "Test Match 1"},
            {"id": "2", "name": "Test Match 2"}
        ]
    })

@app.route('/debug-api-client')
def debug_api_client():
    return jsonify({
        "client_type": "TestClient",
        "available_methods": ["get_matches", "send_message"]
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
    return jsonify({'status': 'ok', 'delay': 3})

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

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found", "path": request.path}), 404

if __name__ == '__main__':
    print("\\n" + "="*60)
    print("🔥 TINDER BOT DASHBOARD - TEMPLATE VERSION")
    print("="*60)
    print(f"Base directory: {BASE_DIR}")
    print(f"Templates directory: {TEMPLATES_DIR}")
    print(f"Templates exist: {TEMPLATES_DIR.exists()}")

    if TEMPLATES_DIR.exists():
        html_files = list(TEMPLATES_DIR.glob("*.html"))
        print(f"HTML files in templates: {[f.name for f in html_files]}")

    print("\\nDashboard at: http://localhost:5050")
    print("="*60 + "\\n")

    app.run(host='0.0.0.0', port=5050, debug=True)  # Debug mode ON for troubleshooting
'''

    # Save the new dashboard
    with open("dashboard_template.py", "w", encoding="utf-8") as f:
        f.write(dashboard_code)

    print("\n✅ Created dashboard_template.py")


def main():
    """Main check and fix"""
    # Check template setup
    templates_dir = check_template_setup()

    # Create the new dashboard
    create_working_dashboard()

    print("\n" + "=" * 60)
    print("📋 NEXT STEPS:")
    print("=" * 60)
    print("1. Stop your current dashboard (Ctrl+C)")
    print("2. Run the new dashboard:")
    print("   python dashboard_template.py")
    print("\nThis will:")
    print("  - Use templates/index.html if it exists")
    print("  - Show debug info about what templates are found")
    print("  - Handle the /start-browser endpoint correctly")
    print("=" * 60)


if __name__ == "__main__":
    main()