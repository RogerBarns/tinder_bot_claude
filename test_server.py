print("Testing imports...")

try:
    from flask import Flask
    print("✅ Flask imported")
except ImportError as e:
    print(f"❌ Flask import failed: {e}")

try:
    from flask_socketio import SocketIO
    print("✅ Flask-SocketIO imported")
except ImportError as e:
    print(f"❌ Flask-SocketIO import failed: {e}")

try:
    from config import config
    print(f"✅ Config imported - sleep schedule: {config.get('respect_sleep_schedule')}")
except ImportError as e:
    print(f"❌ Config import failed: {e}")

try:
    from web.app import app
    print("✅ Web app imported")
except ImportError as e:
    print(f"❌ Web app import failed: {e}")

print("Test complete!")