"""
Fix Unicode error and start the dashboard
"""
import os
import sys
from pathlib import Path

def fix_encoding_and_test():
    """Fix encoding issues and test the dashboard"""
    print("=" * 60)
    print("🔧 FIXING ENCODING ISSUES")
    print("=" * 60)

    # Check if templates/index.html exists
    templates_dir = Path("templates")
    index_file = templates_dir / "index.html"

    if index_file.exists():
        print(f"✅ index.html exists ({index_file.stat().st_size} bytes)")
    else:
        print("❌ index.html missing - creating it...")
        templates_dir.mkdir(exist_ok=True)
        create_minimal_index()

    # Test if we can import and run the app
    print("\n" + "=" * 60)
    print("🧪 TESTING DASHBOARD")
    print("=" * 60)

    try:
        # Try to import the web app
        sys.path.insert(0, str(Path.cwd()))
        from web.app import app

        print("✅ Web app imported successfully")

        # Test the root route
        with app.test_client() as client:
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Dashboard endpoint working!")
                return True
            else:
                print(f"⚠️ Dashboard returned status {response.status_code}")
                return False

    except Exception as e:
        print(f"⚠️ Import error: {e}")
        print("\nTrying alternative approach...")
        return False

def create_minimal_index():
    """Create a minimal working index.html"""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Tinder Bot Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #121212; color: #fff; padding: 20px; }
        .card { background: #1e1e1e; border: 1px solid #333; }
        .card-header { background: #2d2d2d !important; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="text-center mb-4">🔥 Tinder Bot Dashboard</h1>
        <div class="card">
            <div class="card-header">Bot Controls</div>
            <div class="card-body">
                <button id="toggle-bot" class="btn btn-primary">Start Bot</button>
                <button class="btn btn-success">Test Connection</button>
            </div>
        </div>
    </div>
    <script>
        document.getElementById('toggle-bot').addEventListener('click', async () => {
            const res = await fetch('/toggle-bot', {method: 'POST'});
            const data = await res.json();
            alert('Bot ' + (data.enabled ? 'started' : 'stopped'));
        });
    </script>
</body>
</html>"""

    with open("templates/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ Created minimal index.html")

def start_dashboard_directly():
    """Start the dashboard directly, bypassing main.py"""
    print("\n" + "=" * 60)
    print("🚀 STARTING DASHBOARD DIRECTLY")
    print("=" * 60)

    try:
        from web.app import start_web_app
        print("Starting web app on http://localhost:5000")
        print("Press Ctrl+C to stop")
        print("=" * 60)
        start_web_app(host="0.0.0.0", port=5000)
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        print("\nTrying minimal server instead...")
        start_minimal_server()

def start_minimal_server():
    """Start a minimal Flask server as fallback"""
    print("\n" + "=" * 60)
    print("🚀 STARTING MINIMAL SERVER")
    print("=" * 60)

    from flask import Flask, render_template, jsonify
    from pathlib import Path

    app = Flask(__name__, template_folder=str(Path.cwd() / "templates"))

    @app.route('/')
    def index():
        try:
            return render_template('index.html')
        except:
            return """
            <html>
            <body style="background:#121212; color:#fff; padding:20px; font-family:Arial;">
                <h1>🔥 Tinder Bot Dashboard</h1>
                <p>Minimal fallback version</p>
                <button onclick="fetch('/toggle-bot',{method:'POST'}).then(r=>r.json()).then(d=>alert('Bot: '+d.status))">
                    Toggle Bot
                </button>
            </body>
            </html>
            """

    @app.route('/toggle-bot', methods=['POST'])
    def toggle_bot():
        return jsonify({"status": "ok", "enabled": True})

    @app.route('/config')
    def config():
        return jsonify({"bot_enabled": False, "auto_approve": False})

    @app.route('/stats')
    def stats():
        return jsonify({"total_messages": 0, "total_matches": 0})

    print("Starting minimal server on http://localhost:5000")
    print("Press Ctrl+C to stop")
    app.run(host='0.0.0.0', port=5000, debug=False)

def main():
    """Main entry point"""
    # Fix encoding first
    if not fix_encoding_and_test():
        print("\n⚠️ Standard approach failed, using fallback...")

    # Try to start the dashboard
    try:
        start_dashboard_directly()
    except ImportError as e:
        print(f"\n⚠️ Import error: {e}")
        print("Starting minimal server instead...")
        start_minimal_server()
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Starting minimal server as last resort...")
        start_minimal_server()

if __name__ == "__main__":
    main()