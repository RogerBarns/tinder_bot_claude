@echo off
title Tinder Bot Dashboard
color 0A

echo ===============================================
echo         TINDER BOT DASHBOARD LAUNCHER
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

:: Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created.
    echo.
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Install/upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1

:: Check and install required packages
echo Checking dependencies...
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Flask...
    pip install flask
)

python -c "import flask_socketio" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Flask-SocketIO...
    pip install flask-socketio
)

python -c "import apscheduler" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing APScheduler...
    pip install apscheduler
)

python -c "import dotenv" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing python-dotenv...
    pip install python-dotenv
)

python -c "import requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing requests...
    pip install requests
)

:: Clear screen before starting
cls
echo ===============================================
echo         TINDER BOT DASHBOARD
echo ===============================================
echo.
echo Starting bot in 3 seconds...
echo.
echo Dashboard will be available at:
echo   http://localhost:5000
echo.
echo Press Ctrl+C to stop the bot
echo ===============================================
echo.

timeout /t 3 /nobreak >nul

:: Run the bot
python main.py

:: If bot crashes, keep window open
if %errorlevel% neq 0 (
    echo.
    echo ===============================================
    echo Bot stopped with error code: %errorlevel%
    echo ===============================================
    pause
)

:: Deactivate virtual environment
deactivate

pause