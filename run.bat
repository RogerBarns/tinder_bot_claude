@echo off
echo Starting Tinder Bot...
echo.

REM Set the specific Python executable path
set PYTHON_EXE="C:\Program Files\Python313\python.exe"

REM Verify Python exists
if not exist %PYTHON_EXE% (
    echo ERROR: Python 3.13 not found at %PYTHON_EXE%
    echo Please check your Python installation path
    pause
    exit /b 1
)

REM Test if browser dependencies are available
echo Checking browser automation dependencies...
%PYTHON_EXE% -c "import undetected_chromedriver, selenium; print('✅ Browser automation ready!')" 2>nul
if errorlevel 1 (
    echo ⚠️ Browser dependencies not found, bot will run in stub mode
    echo To enable browser automation, run:
    echo %PYTHON_EXE% -m pip install undetected-chromedriver selenium
    echo.
) else (
    echo ✅ Browser automation dependencies found!
    echo.
)

REM Skip virtual environment since we're using specific Python
REM Comment out the venv section since packages are installed system-wide
REM if exist venv\Scripts\activate.bat (
REM     call venv\Scripts\activate.bat
REM ) else (
REM     echo NOTE: No virtual environment found, using system Python
REM )

REM Check if .env exists
if not exist .env (
    echo ERROR: .env file not found!
    echo Please copy .env.template to .env and add your API keys
    pause
    exit /b 1
)

REM Check for Claude API key (Tinder token not needed for browser mode)
findstr "your_claude_api_key_here" .env >nul
if not errorlevel 1 (
    echo ERROR: Please update CLAUDE_API_KEY in .env file!
    echo.
    echo Get your API key from: https://console.anthropic.com/
    echo.
    pause
    exit /b 1
)

REM Check for Tinder token but don't require it (browser mode doesn't need it)
findstr "your_tinder_auth_token_here" .env >nul
if not errorlevel 1 (
    echo NOTE: TINDER_AUTH_TOKEN not set (OK for browser mode)
    echo If you want to use API mode instead of browser, set this token
    echo.
)

REM Clear screen and start bot
cls
echo ============================================
echo  Tinder Bot Starting...
echo ============================================
echo.
echo Using Python: %PYTHON_EXE%
echo Dashboard will be available at: http://localhost:5000
echo Press Ctrl+C to stop the bot
echo.
echo Starting in 3 seconds...
timeout /t 3 /nobreak >nul

REM Run the bot with the specific Python executable
%PYTHON_EXE% main.py

echo.
echo Bot stopped.
pause