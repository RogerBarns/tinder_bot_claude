@echo off
echo ============================================
echo  Tinder Bot Setup for Windows 11
echo ============================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8 or higher
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/7] Creating virtual environment...
python -m venv venv

echo [2/7] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/7] Upgrading pip...
python -m pip install --upgrade pip

echo [4/7] Installing requirements...
pip install -r requirements-windows.txt

echo [5/7] Creating project directories...
if not exist "models" mkdir models
if not exist "core" mkdir core
if not exist "personality" mkdir personality
if not exist "utils" mkdir utils
if not exist "web" mkdir web
if not exist "templates" mkdir templates
if not exist "static" mkdir static
if not exist "data" mkdir data
if not exist "logs" mkdir logs

echo [6/7] Creating __init__.py files...
type nul > models\__init__.py
type nul > core\__init__.py
type nul > personality\__init__.py
type nul > utils\__init__.py
type nul > web\__init__.py

echo [7/7] Creating .env file from template...
if not exist .env (
    (
        echo # Tinder Bot Configuration
        echo # Copy this to .env and fill in your actual values
        echo.
        echo # Tinder API Authentication
        echo TINDER_AUTH_TOKEN=your_tinder_auth_token_here
        echo.
        echo # Your Tinder User ID
        echo MY_USER_ID=your_tinder_user_id_here
        echo.
        echo # Claude API Key from Anthropic
        echo CLAUDE_API_KEY=sk-ant-api03-your-key-here
        echo.
        echo # Optional: Account identifier
        echo TINDER_ACCOUNT_ID=main
    ) > .env
    echo.
    echo IMPORTANT: Please edit .env file with your API keys!
) else (
    echo .env file already exists
)

echo.
echo ============================================
echo  Setup complete!
echo ============================================
echo.
echo Next steps:
echo 1. Edit .env file with your API keys
echo 2. Run: run.bat
echo 3. Open http://localhost:5000 in your browser
echo.
pause