@echo off
title Tinder Bot Dashboard
color 0A

echo ===============================================
echo     TINDER BOT DASHBOARD LAUNCHER
echo ===============================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Checking required packages...
echo.

:: Install/upgrade required packages
python -m pip install --upgrade pip >nul 2>&1
python -m pip install flask flask-socketio python-dotenv requests >nul 2>&1

echo ===============================================
echo     STARTING TINDER BOT DASHBOARD
echo ===============================================
echo.

:: Check which dashboard file exists and run it
if exist "simple_dashboard.py" (
    echo Starting simple_dashboard.py...
    echo.
    echo Dashboard will be available at:
    echo   http://localhost:5050
    echo.
    echo Press Ctrl+C to stop the bot
    echo ===============================================
    echo.
    python simple_dashboard.py
) else if exist "dashboard.py" (
    echo Starting dashboard.py...
    echo.
    echo Dashboard will be available at:
    echo   http://localhost:5050
    echo.
    echo Press Ctrl+C to stop the bot
    echo ===============================================
    echo.
    python dashboard.py
) else (
    echo Creating and starting minimal dashboard...
    echo.
    
    :: Create a minimal dashboard if none exists
    (
    echo from flask import Flask, jsonify, render_template_string
    echo import random
    echo.
    echo app = Flask(__name__^)
    echo.
    echo @app.route('/'^^^)
    echo def index(^^^):
    echo     return '''
    echo     ^<!DOCTYPE html^>
    echo     ^<html^>
    echo     ^<head^>^<title^>Tinder Bot^</title^>^</head^>
    echo     ^<body style="background:#1a1a1a;color:white;text-align:center;padding:50px;"^>
    echo         ^<h1^>Tinder Bot Dashboard^</h1^>
    echo         ^<button onclick="fetch('/toggle-bot',{method:'POST'}).then(r=^>r.json()).then(d=^>alert('Bot: '+d.enabled))"^>Toggle Bot^</button^>
    echo     ^</body^>
    echo     ^</html^>
    echo     '''
    echo.
    echo @app.route('/toggle-bot', methods=['POST']^^^)
    echo def toggle_bot(^^^):
    echo     return jsonify({"enabled": True}^^^)
    echo.
    echo @app.route('/config'^^^)
    echo def config(^^^):
    echo     return jsonify({"bot_enabled": False}^^^)
    echo.
    echo @app.route('/stats'^^^)
    echo def stats(^^^):
    echo     return jsonify({"total_messages": 0}^^^)
    echo.
    echo if __name__ == '__main__':
    echo     print("Dashboard at: http://localhost:5050"^^^)
    echo     app.run(host='0.0.0.0', port=5050, debug=False^^^)
    ) > temp_dashboard.py
    
    echo Dashboard will be available at:
    echo   http://localhost:5050
    echo.
    echo Press Ctrl+C to stop the bot
    echo ===============================================
    echo.
    python temp_dashboard.py
    
    :: Clean up temp file
    del temp_dashboard.py >nul 2>&1
)

if %errorlevel% neq 0 (
    echo.
    echo ===============================================
    echo Bot stopped or encountered an error
    echo ===============================================
    echo.
    echo If you see an error above, try:
    echo 1. Make sure all packages are installed:
    echo    pip install flask flask-socketio
    echo.
    echo 2. Check if port 5050 is already in use
    echo.
    echo 3. Run the dashboard directly:
    echo    python simple_dashboard.py
    echo ===============================================
)

pause