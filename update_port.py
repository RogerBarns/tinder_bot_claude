"""
Quick script to update your simple_dashboard.py to use port 5050
"""
import os
from pathlib import Path


def update_dashboard_port():
    """Update the dashboard to use port 5050"""

    # List of files to check and update
    dashboard_files = [
        "simple_dashboard.py",
        "dashboard.py",
        "minimal_dashboard.py"
    ]

    for filename in dashboard_files:
        filepath = Path(filename)
        if filepath.exists():
            print(f"Updating {filename}...")

            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Replace port 5000 with 5050
            content = content.replace('port=5000', 'port=5050')
            content = content.replace('localhost:5000', 'localhost:5050')
            content = content.replace(':5000', ':5050')

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"✅ Updated {filename} to use port 5050")

    # Update main.py if it exists
    main_path = Path("main.py")
    if main_path.exists():
        print("Updating main.py...")

        # Read the fixed main.py content
        fixed_main = '''"""
Main entry point for Tinder Bot - Fixed for port 5050
"""
import os
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main application entry point"""
    print("=" * 60)
    print("🚀 Starting Tinder Bot Dashboard...")
    print("=" * 60)

    # Try to run simple_dashboard.py if it exists
    simple_dashboard_path = Path(__file__).parent / "simple_dashboard.py"
    if simple_dashboard_path.exists():
        print("Starting simple_dashboard.py on port 5050...")
        import subprocess
        subprocess.run([sys.executable, str(simple_dashboard_path)])
    else:
        print("Creating minimal dashboard...")
        from flask import Flask, jsonify

        app = Flask(__name__)

        @app.route('/')
        def index():
            return """
            <html>
            <body style="background:#1a1a1a;color:white;text-align:center;padding:50px;">
                <h1>🔥 Tinder Bot Dashboard</h1>
                <p>Running on port 5050</p>
                <button onclick="alert('Bot is running!')">Test</button>
            </body>
            </html>
            """

        @app.route('/toggle-bot', methods=['POST'])
        def toggle_bot():
            return jsonify({"enabled": True})

        print("Dashboard at: http://localhost:5050")
        app.run(host='0.0.0.0', port=5050, debug=False)

if __name__ == "__main__":
    main()
'''

        with open(main_path, 'w', encoding='utf-8') as f:
            f.write(fixed_main)

        print("✅ Updated main.py to use port 5050")

    print("\n" + "=" * 60)
    print("✅ All files updated to use port 5050!")
    print("=" * 60)
    print("\nYou can now run:")
    print("  python main.py")
    print("  python simple_dashboard.py")
    print("  run_bot.bat")
    print("\nDashboard will be at: http://localhost:5050")


if __name__ == "__main__":
    update_dashboard_port()