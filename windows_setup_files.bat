# setup.bat - Windows Setup Script
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
    copy .env.template .env
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


# run.bat - Windows Run Script
@echo off
echo Starting Tinder Bot...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if .env exists
if not exist .env (
    echo ERROR: .env file not found!
    echo Please copy .env.template to .env and add your API keys
    pause
    exit /b 1
)

REM Check for placeholder values
findstr "your_tinder_auth_token_here" .env >nul
if not errorlevel 1 (
    echo ERROR: Please update TINDER_AUTH_TOKEN in .env file!
    pause
    exit /b 1
)

findstr "your_claude_api_key_here" .env >nul
if not errorlevel 1 (
    echo ERROR: Please update CLAUDE_API_KEY in .env file!
    pause
    exit /b 1
)

REM Clear screen and start bot
cls
echo ============================================
echo  Tinder Bot Starting...
echo ============================================
echo.
echo Dashboard will be available at: http://localhost:5000
echo Press Ctrl+C to stop the bot
echo.

python main.py

pause


# install.ps1 - PowerShell Installation Script (Alternative)
# Run with: powershell -ExecutionPolicy Bypass -File install.ps1

Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Tinder Bot Setup for Windows 11 (PowerShell)" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found! Please install Python 3.8+" -ForegroundColor Red
    Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install requirements
Write-Host "Installing requirements..." -ForegroundColor Yellow
pip install -r requirements-windows.txt

# Create directories
Write-Host "Creating project directories..." -ForegroundColor Yellow
$dirs = @("models", "core", "personality", "utils", "web", "templates", "static", "data", "logs")
foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}

# Create __init__.py files
Write-Host "Creating __init__.py files..." -ForegroundColor Yellow
$initDirs = @("models", "core", "personality", "utils", "web")
foreach ($dir in $initDirs) {
    New-Item -ItemType File -Force -Path "$dir\__init__.py" | Out-Null
}

# Copy .env template
if (!(Test-Path ".env")) {
    Copy-Item ".env.template" ".env"
    Write-Host ""
    Write-Host "IMPORTANT: Please edit .env file with your API keys!" -ForegroundColor Red
} else {
    Write-Host ".env file already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Setup complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env file with your API keys"
Write-Host "2. Run: .\run.ps1 or run.bat"
Write-Host "3. Open http://localhost:5000 in your browser"
Write-Host ""
Read-Host "Press Enter to exit"


# run.ps1 - PowerShell Run Script
Write-Host "Starting Tinder Bot..." -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
& ".\venv\Scripts\Activate.ps1"

# Check .env exists
if (!(Test-Path ".env")) {
    Write-Host "ERROR: .env file not found!" -ForegroundColor Red
    Write-Host "Please copy .env.template to .env and add your API keys" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check for placeholder values
$envContent = Get-Content ".env"
if ($envContent -match "your_tinder_auth_token_here") {
    Write-Host "ERROR: Please update TINDER_AUTH_TOKEN in .env file!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

if ($envContent -match "your_claude_api_key_here") {
    Write-Host "ERROR: Please update CLAUDE_API_KEY in .env file!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Clear-Host
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Tinder Bot Starting..." -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Dashboard will be available at: " -NoNewline
Write-Host "http://localhost:5000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the bot" -ForegroundColor Yellow
Write-Host ""

python main.py