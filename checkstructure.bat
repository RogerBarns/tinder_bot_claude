@echo off
echo Checking Tinder Bot Structure...
echo ================================
echo.
tree /F /A
echo.
echo ================================
echo Checking for required files...
echo ================================
echo.

if exist run.bat (echo [OK] run.bat) else (echo [MISSING] run.bat)
if exist setup.bat (echo [OK] setup.bat) else (echo [MISSING] setup.bat)
if exist .env (echo [OK] .env) else (echo [MISSING] .env)
if exist main.py (echo [OK] main.py) else (echo [MISSING] main.py)
if exist config.py (echo [OK] config.py) else (echo [MISSING] config.py)
if exist models\session.py (echo [OK] models\session.py) else (echo [MISSING] models\session.py)
if exist core\api_client.py (echo [OK] core\api_client.py) else (echo [MISSING] core\api_client.py)
if exist web\app.py (echo [OK] web\app.py) else (echo [MISSING] web\app.py)
if exist templates\index.html (echo [OK] templates\index.html) else (echo [MISSING] templates\index.html)

echo.
pause